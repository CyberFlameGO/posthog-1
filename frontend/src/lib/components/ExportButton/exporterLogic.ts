import { actions, kea, key, listeners, path, props, reducers } from 'kea'
import api from 'lib/api'
import { teamLogic } from 'scenes/teamLogic'
import { InsightModel } from '~/types'
import { lemonToast } from '../lemonToast'

import type { exporterLogicType } from './exporterLogicType'

interface ExporterLogicProps {
    insight: InsightModel
}
export const exporterLogic = kea<exporterLogicType<ExporterLogicProps>>([
    path(['lib', 'components', 'ExportButton', 'ExporterLogic']),
    props({} as ExporterLogicProps),
    key(({ insight }) => {
        if (!insight.short_id) {
            throw Error('must provide an insight with a short id')
        }
        return insight.short_id
    }),
    actions({
        exportInsight: (successCallback?: () => void) => ({ successCallback }),
        exportInsightSuccess: true,
        exportInsightFailure: true,
    }),

    reducers({
        exportInProgress: [
            false,
            {
                exportInsight: () => true,
                exportInsightSuccess: () => false,
                exportInsightFailure: () => false,
            },
        ],
    }),

    listeners(({ actions, props }) => ({
        exportInsight: async ({ successCallback }, breakpoint) => {
            await breakpoint(1000)

            lemonToast.info(`Export of Insight ${props.insight.name ?? props.insight.derived_name} started...`)

            try {
                await api.create(`api/projects/${teamLogic.values.currentTeamId}/insights/${props.insight.id}/export`)
                actions.exportInsightSuccess()
                successCallback?.()
            } catch (e) {
                actions.exportInsightFailure()
                lemonToast.error(`Export of Insight ${props.insight.name ?? props.insight.derived_name} failed.`)
            }
        },
    })),
])
