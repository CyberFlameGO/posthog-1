import { actions, kea, key, listeners, path, props, reducers } from 'kea'
import api from 'lib/api'
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
                // NOTE: This endpoint should maybe be more specific
                await api.create(`api/projects/${teamLogic.values.currentTeamId}/${props.type}s/${props.id}/exports`)

                // TODO: Start polling the retrieval endpoint up to N times...
                actions.exportItemSuccess()
                lemonToast.success(`Export of ${props.type} complete.`)
                successCallback?.()
            } catch (e) {
                actions.exportItemFailure()
                lemonToast.error(`Export of ${props.type} failed.`)
            }
        },
    })),
])
