import React from 'react'
import ReactDOM from 'react-dom'
import { initKea } from '~/initKea'
import { Dashboard } from './Dashboard'
import { loadPostHogJS } from '~/loadPostHogJS'
import { FriendlyLogo } from '~/toolbar/assets/FriendlyLogo'
import '~/styles'
import './DashboardItems.scss'
import { DashboardPlacement } from '~/types'

loadPostHogJS()
initKea()

const dashboard = (window as any).__SHARED_DASHBOARD__
const isEmbedded = window.location.search.includes('embedded')

ReactDOM.render(
    <>
        <div style={{ minHeight: '100vh', top: 0, padding: !isEmbedded ? '1rem' : '0.5rem 1rem' }}>
            {!isEmbedded ? (
                <div className="space-between-items items-center space-x ">
                    <a href="https://posthog.com" target="_blank" rel="noopener noreferrer">
                        <FriendlyLogo style={{ fontSize: '1.125rem' }} />
                    </a>
                    <div className="text-center" style={{ maxWidth: '50%' }}>
                        <h1 className="mb-05" data-attr="dashboard-item-title">
                            {dashboard.name}
                        </h1>
                        <span>{dashboard.description}</span>
                    </div>
                    <span>{dashboard.team_name}</span>
                </div>
            ) : (
                <a
                    href="https://posthog.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ display: 'block', marginBottom: '-3rem' }}
                >
                    <FriendlyLogo style={{ fontSize: '1.125rem' }} />
                </a>
            )}

            <Dashboard id={dashboard.id} shareToken={dashboard.share_token} placement={DashboardPlacement.Public} />

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
    </>,
    document.getElementById('root')
)
