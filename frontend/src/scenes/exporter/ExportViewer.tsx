import React from 'react'
import ReactDOM from 'react-dom'
import { initKea } from '~/initKea'
import { Dashboard } from '../dashboard/Dashboard'
import { loadPostHogJS } from '~/loadPostHogJS'
import { FriendlyLogo } from '~/toolbar/assets/FriendlyLogo'
import '~/styles'
import '../dashboard/DashboardItems.scss'
import { DashboardPlacement } from '~/types'

// Disable tracking for exporting
window.JS_POSTHOG_API_KEY = null
loadPostHogJS()
initKea()

const dashboard = (window as any).__SHARED_DASHBOARD__

const ExportViewer = (): JSX.Element => {
    return (
        <div className="pa" style={{ minHeight: '100vh' }}>
            <Dashboard id={dashboard.id} shareToken={dashboard.share_token} placement={DashboardPlacement.Export} />

            <div>
                <FriendlyLogo style={{ fontSize: '1.125rem' }} />
            </div>
            <div className="text-center pb">
                Made with{' '}
                <a
                    href="https://posthog.com?utm_medium=in-product&utm_campaign=shared-dashboard"
                    target="_blank"
                    rel="noopener"
                >
                    PostHog – open-source product analytics
                </a>
            </div>
        </div>
    )
}

ReactDOM.render(<ExportViewer />, document.getElementById('root'))
