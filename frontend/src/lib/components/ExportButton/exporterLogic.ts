import { actions, kea, key, listeners, path, props, reducers } from 'kea'
import api from 'lib/api'
import { delay } from 'lib/utils'
import { teamLogic } from 'scenes/teamLogic'
import { lemonToast } from '../lemonToast'

import type { exporterLogicType } from './exporterLogicType'

export interface ExporterLogicProps {
    type: 'dashboard' | 'insight'
    id: string
}
export const exporterLogic = kea<exporterLogicType<ExporterLogicProps>>([
    path(['lib', 'components', 'ExportButton', 'ExporterLogic']),
    props({} as ExporterLogicProps),
    key(({ id, type }) => {
        return `${id}:${type}`
    }),
    actions({
        exportItem: (successCallback?: () => void) => ({ successCallback }),
        exportItemSuccess: true,
        exportItemFailure: true,
    }),

    reducers({
        exportInProgress: [
            false,
            {
                exportItem: () => true,
                exportItemSuccess: () => false,
                exportItemFailure: () => false,
            },
        ],
    }),

    listeners(({ actions, props }) => ({
        exportItem: async ({ successCallback }, breakpoint) => {
            lemonToast.info(`Export of ${props.type}  started...`)

            await breakpoint(1000)

            try {
                const { export_id } = await api.create(
                    `api/projects/${teamLogic.values.currentTeamId}/${props.type}s/${props.id}/exports`
                )

                if (!export_id) {
                    throw new Error('Missin export_id from response')
                }

                const downloadUrl = api.exports.determineExportUrl(export_id)

                let attempts = 0

                // TODO: Move this to some sort of Kea-style polling
                while (attempts < 20) {
                    attempts++

                    const { has_content } = await api.get(
                        `api/projects/${teamLogic.values.currentTeamId}/exports/${export_id}`
                    )

                    await delay(2000)

                    if (has_content) {
                        actions.exportItemSuccess()
                        lemonToast.success(`Export of ${props.type} complete.`)
                        successCallback?.()

                        console.log('should open ', downloadUrl)

                        window.open(downloadUrl, '_blank')

                        return
                    }
                }

                throw new Error('Content not loaded in time...')
            } catch (e) {
                actions.exportItemFailure()
                lemonToast.error(`Export of ${props.type} failed.`)
            }
        },
    })),
])
