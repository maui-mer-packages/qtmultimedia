/****************************************************************************
**
** Copyright (C) 2012 Nokia Corporation and/or its subsidiary(-ies).
** Copyright (C) 2012 Research In Motion
** Contact: http://www.qt-project.org/
**
** This file is part of the Qt Toolkit.
**
** $QT_BEGIN_LICENSE:LGPL$
** GNU Lesser General Public License Usage
** This file may be used under the terms of the GNU Lesser General Public
** License version 2.1 as published by the Free Software Foundation and
** appearing in the file LICENSE.LGPL included in the packaging of this
** file. Please review the following information to ensure the GNU Lesser
** General Public License version 2.1 requirements will be met:
** http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html.
**
** In addition, as a special exception, Nokia gives you certain additional
** rights. These rights are described in the Nokia Qt LGPL Exception
** version 1.1, included in the file LGPL_EXCEPTION.txt in this package.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU General
** Public License version 3.0 as published by the Free Software Foundation
** and appearing in the file LICENSE.GPL included in the packaging of this
** file. Please review the following information to ensure the GNU General
** Public License version 3.0 requirements will be met:
** http://www.gnu.org/copyleft/gpl.html.
**
** Other Usage
** Alternatively, this file may be used in accordance with the terms and
** conditions contained in a signed written agreement between you and Nokia.
**
**
**
**
**
**
** $QT_END_LICENSE$
**
****************************************************************************/

#include "qdeclarativevideooutput_render_p.h"
#include "qdeclarativevideooutput_p.h"
#include <QtMultimedia/qvideorenderercontrol.h>
#include <QtMultimedia/qmediaservice.h>
#include <private/qmediapluginloader_p.h>
#include <private/qsgvideonode_p.h>

QT_BEGIN_NAMESPACE

Q_GLOBAL_STATIC_WITH_ARGS(QMediaPluginLoader, videoNodeFactoryLoader,
        (QSGVideoNodeFactoryInterface_iid, QLatin1String("video/videonode"), Qt::CaseInsensitive))

QDeclarativeVideoRendererBackend::QDeclarativeVideoRendererBackend(QDeclarativeVideoOutput *parent)
    : QDeclarativeVideoBackend(parent),
      m_frameChanged(false)
{
    m_surface = new QSGVideoItemSurface(this);
    QObject::connect(m_surface, SIGNAL(surfaceFormatChanged(QVideoSurfaceFormat)),
                     q, SLOT(_q_updateNativeSize()), Qt::QueuedConnection);

    foreach (QObject *instance, videoNodeFactoryLoader()->instances(QSGVideoNodeFactoryPluginKey)) {
        QSGVideoNodeFactoryInterface* plugin = qobject_cast<QSGVideoNodeFactoryInterface*>(instance);
        if (plugin)
            m_videoNodeFactories.append(plugin);
    }

    // Append existing node factories as fallback if we have no plugins
    m_videoNodeFactories.append(&m_i420Factory);
    m_videoNodeFactories.append(&m_rgbFactory);
}

QDeclarativeVideoRendererBackend::~QDeclarativeVideoRendererBackend()
{
    releaseSource();
    releaseControl();
    delete m_surface;
}

bool QDeclarativeVideoRendererBackend::init(QMediaService *service)
{
    // When there is no service, the source is an object with a "videoSurface" property, which
    // doesn't require a QVideoRendererControl and therefore always works
    if (!service)
        return true;

    if (QMediaControl *control = service->requestControl(QVideoRendererControl_iid)) {
        if ((m_rendererControl = qobject_cast<QVideoRendererControl *>(control))) {
            m_rendererControl->setSurface(m_surface);
            m_service = service;
            return true;
        }
    }
    return false;
}

void QDeclarativeVideoRendererBackend::itemChange(QQuickItem::ItemChange change,
                                      const QQuickItem::ItemChangeData &changeData)
{
    Q_UNUSED(change);
    Q_UNUSED(changeData);
}

void QDeclarativeVideoRendererBackend::releaseSource()
{
    if (q->source() && q->sourceType() == QDeclarativeVideoOutput::VideoSurfaceSource) {
        if (q->source()->property("videoSurface").value<QAbstractVideoSurface*>() == m_surface)
            q->source()->setProperty("videoSurface", QVariant::fromValue<QAbstractVideoSurface*>(0));
    }

    m_surface->stop();
}

void QDeclarativeVideoRendererBackend::releaseControl()
{
    if (m_rendererControl) {
        m_rendererControl->setSurface(0);
        if (m_service)
            m_service->releaseControl(m_rendererControl);
        m_rendererControl = 0;
    }
}

QSize QDeclarativeVideoRendererBackend::nativeSize() const
{
    return m_surface->surfaceFormat().sizeHint();
}

void QDeclarativeVideoRendererBackend::updateGeometry()
{
    const QRectF rect(0, 0, q->width(), q->height());
    if (nativeSize().isEmpty()) {
        m_renderedRect = rect;
        m_sourceTextureRect = QRectF(0, 0, 1, 1);
    } else if (q->fillMode() == QDeclarativeVideoOutput::Stretch) {
        m_renderedRect = rect;
        m_sourceTextureRect = QRectF(0, 0, 1, 1);
    } else if (q->fillMode() == QDeclarativeVideoOutput::PreserveAspectFit) {
        m_sourceTextureRect = QRectF(0, 0, 1, 1);
        m_renderedRect = q->contentRect();
    } else if (q->fillMode() == QDeclarativeVideoOutput::PreserveAspectCrop) {
        m_renderedRect = rect;
        const qreal contentHeight = q->contentRect().height();
        const qreal contentWidth = q->contentRect().width();
        if (qIsDefaultAspect(q->orientation())) {
            m_sourceTextureRect = QRectF(-q->contentRect().left() / contentWidth,
                                         -q->contentRect().top() / contentHeight,
                                         rect.width() / contentWidth,
                                         rect.height() / contentHeight);
        } else {
            m_sourceTextureRect = QRectF(-q->contentRect().top() / contentHeight,
                                         -q->contentRect().left() / contentWidth,
                                         rect.height() / contentHeight,
                                         rect.width() / contentWidth);
        }
    }
}

QSGNode *QDeclarativeVideoRendererBackend::updatePaintNode(QSGNode *oldNode,
                                                           QQuickItem::UpdatePaintNodeData *data)
{
    Q_UNUSED(data);
    QSGVideoNode *videoNode = static_cast<QSGVideoNode *>(oldNode);

    QMutexLocker lock(&m_frameMutex);

    if (m_frameChanged) {
        if (videoNode && videoNode->pixelFormat() != m_frame.pixelFormat()) {
#ifdef DEBUG_VIDEOITEM
            qDebug() << "updatePaintNode: deleting old video node because frame format changed...";
#endif
            delete videoNode;
            videoNode = 0;
        }

        if (!m_frame.isValid()) {
#ifdef DEBUG_VIDEOITEM
            qDebug() << "updatePaintNode: no frames yet... aborting...";
#endif
            m_frameChanged = false;
            return 0;
        }

        if (!videoNode) {
            foreach (QSGVideoNodeFactoryInterface* factory, m_videoNodeFactories) {
                videoNode = factory->createNode(m_surface->surfaceFormat());
                if (videoNode)
                    break;
            }
        }
    }

    if (!videoNode) {
        m_frameChanged = false;
        m_frame = QVideoFrame();
        return 0;
    }

    // Negative rotations need lots of %360
    videoNode->setTexturedRectGeometry(m_renderedRect, m_sourceTextureRect,
                                       qNormalizedOrientation(q->orientation()));
    if (m_frameChanged) {
        videoNode->setCurrentFrame(m_frame);
        //don't keep the frame for more than really necessary
        m_frameChanged = false;
        m_frame = QVideoFrame();
    }
    return videoNode;
}

QAbstractVideoSurface *QDeclarativeVideoRendererBackend::videoSurface() const
{
    return m_surface;
}

void QDeclarativeVideoRendererBackend::present(const QVideoFrame &frame)
{
    m_frameMutex.lock();
    m_frame = frame;
    m_frameChanged = true;
    m_frameMutex.unlock();

    q->update();
}

void QDeclarativeVideoRendererBackend::stop()
{
    present(QVideoFrame());
}

QSGVideoItemSurface::QSGVideoItemSurface(QDeclarativeVideoRendererBackend *backend, QObject *parent)
    : QAbstractVideoSurface(parent),
      m_backend(backend)
{
}

QSGVideoItemSurface::~QSGVideoItemSurface()
{
}

QList<QVideoFrame::PixelFormat> QSGVideoItemSurface::supportedPixelFormats(
        QAbstractVideoBuffer::HandleType handleType) const
{
    QList<QVideoFrame::PixelFormat> formats;

    foreach (QSGVideoNodeFactoryInterface* factory, m_backend->m_videoNodeFactories)
        formats.append(factory->supportedPixelFormats(handleType));

    return formats;
}

bool QSGVideoItemSurface::start(const QVideoSurfaceFormat &format)
{
#ifdef DEBUG_VIDEOITEM
    qDebug() << Q_FUNC_INFO << format;
#endif

    if (!supportedPixelFormats(format.handleType()).contains(format.pixelFormat()))
        return false;

    return QAbstractVideoSurface::start(format);
}

void QSGVideoItemSurface::stop()
{
    m_backend->stop();
    QAbstractVideoSurface::stop();
}

bool QSGVideoItemSurface::present(const QVideoFrame &frame)
{
    if (!frame.isValid()) {
        qWarning() << Q_FUNC_INFO << "I'm getting bad frames here...";
        return false;
    }
    m_backend->present(frame);
    return true;
}

QT_END_NAMESPACE
