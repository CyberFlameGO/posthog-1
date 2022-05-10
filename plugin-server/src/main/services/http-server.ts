import * as Sentry from '@sentry/node'
import { createServer, IncomingMessage, Server, ServerResponse } from 'http'

import { status } from '../../utils/status'
import { kafkaHealthcheck } from '../utils'
import { Hub, PluginsServerConfig } from './../../types'

export const HTTP_SERVER_PORT = 6738

export function createHttpServer(hub: Hub, serverConfig: PluginsServerConfig): Server {
    const server = createServer(async (req: IncomingMessage, res: ServerResponse) => {
        if (req.url === '/_health' && req.method === 'GET') {
            let serverHealthy = true

            if (hub.kafka) {
                const [kafkaHealthy, error] = await kafkaHealthcheck(hub.kafka!)
                if (kafkaHealthy) {
                    status.info('💚', `Kafka healthcheck succeeded`)
                } else {
                    serverHealthy = false
                    Sentry.captureException(error, { tags: { context: 'healthcheck' } })
                    status.info('💔', `Kafka healthcheck failed with error: ${error?.message || 'unknown error'}.`)
                }
            }

            if (serverHealthy) {
                status.info('💚', 'Server healthcheck succeeded')
                const responseBody = {
                    status: 'ok',
                }
                res.statusCode = 200
                res.end(JSON.stringify(responseBody))
            } else {
                status.info('💔', 'Server healthcheck failed')
                const responseBody = {
                    status: 'error',
                }
                res.statusCode = 503
                res.end(JSON.stringify(responseBody))
            }
        }
    })

    server.listen(HTTP_SERVER_PORT, () => {
        status.info('🩺', `Status server listening on port ${HTTP_SERVER_PORT}`)
    })

    return server
}
