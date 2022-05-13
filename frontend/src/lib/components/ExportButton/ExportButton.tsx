import React from 'react'
import { LemonButton } from '../LemonButton'
import { IconExport } from 'lib/components/icons'
import { useActions, useValues } from 'kea'
import { exporterLogic, ExporterLogicProps } from './exporterLogic'

export function ExportButton({ type, id }: ExporterLogicProps): JSX.Element {
    const { exportItem } = useActions(exporterLogic({ type, id }))
    const { exportInProgress } = useValues(exporterLogic({ type, id }))

    const onClick = (): void => {
        exportItem(() => {
            console.log('Should save file')
        })
    }

    return (
        <LemonButton onClick={() => onClick()} type="secondary" icon={<IconExport />} loading={exportInProgress}>
            Export
        </LemonButton>
    )
}
