import React from 'react'
import { InsightModel } from '~/types'
import { LemonButton } from '../LemonButton'
import { IconExport } from 'lib/components/icons'
import { useActions, useValues } from 'kea'
import { exporterLogic } from './exporterLogic'

interface ExportButtonProps {
    insight: InsightModel
}

export function ExportButton({ insight }: ExportButtonProps): JSX.Element {
    // const [openModal, setOpenModal] = useState<boolean>(false)
    const { exportInsight } = useActions(exporterLogic({ insight }))
    const { exportInProgress } = useValues(exporterLogic({ insight }))

    const onClick = (): void => {
        exportInsight(() => {
            alert('DONE!')
        })
    }

    return (
        <LemonButton onClick={() => onClick()} type="secondary" icon={<IconExport />} loading={exportInProgress}>
            Export
        </LemonButton>
    )
}
