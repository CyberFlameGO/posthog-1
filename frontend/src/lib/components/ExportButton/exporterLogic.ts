import { actions, kea, key, listeners, path, props, reducers } from 'kea'
import api from 'lib/api'
import { delay } from 'lib/utils'
import { teamLogic } from 'scenes/teamLogic'
import { lemonToast } from '../lemonToast'

import type { exporterLogicType } from './exporterLogicType'

export interface ExporterLogicProps {
    dashboard_id?: number
    insight_id?: number
}
export const exporterLogic = kea<exporterLogicType<ExporterLogicProps>>([
    path(['lib', 'components', 'ExportButton', 'ExporterLogic']),
    props({} as ExporterLogicProps),
    key(({ dashboard_id, insight_id }) => {
        return `dash:${dashboard_id}::insight:${insight_id}`
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
            lemonToast.info(`Export started...`)

            await breakpoint(1000)

            try {
                let exportedAsset = await api.create(`api/projects/${teamLogic.values.currentTeamId}/exports`, {
                    export_format: 'image/png', // TODO: Make this controlable
                    dashboard: props.dashboard_id,
                    insight: props.insight_id,
                })

                if (!exportedAsset.id) {
                    throw new Error('Missing export_id from response')
                }

                const downloadUrl = api.exports.determineExportUrl(exportedAsset.id)

                let attempts = 0

                // TODO: Move this to some sort of Kea-style polling
                while (attempts < 20) {
                    attempts++

                    exportedAsset = await api.get(
                        `api/projects/${teamLogic.values.currentTeamId}/exports/${exportedAsset.id}`
                    )

                    await delay(2000)

                    if (exportedAsset.has_content) {
                        actions.exportItemSuccess()
                        lemonToast.success(`Export complete.`)
                        successCallback?.()

                        console.log('should open ', downloadUrl)

                        window.open(downloadUrl, '_blank')

                        return
                    }
                }

                throw new Error('Content not loaded in time...')
            } catch (e) {
                actions.exportItemFailure()
                lemonToast.error(`Export failed.`)
            }
        },
    })),
])
