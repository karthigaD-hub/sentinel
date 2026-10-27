import {
  createRootRouteWithContext,
  createRoute,
  Outlet,
  redirect,
} from '@tanstack/react-router'
import { type QueryClient } from '@tanstack/react-query'
import { tokens } from './api/tokens'
import { AppLayout } from './layouts/AppLayout'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { ForgotPasswordPage } from './pages/ForgotPasswordPage'
import { ResetPasswordPage } from './pages/ResetPasswordPage'
import { DashboardPage } from './pages/DashboardPage'
import { PacketMonitoringPage } from './pages/PacketMonitoringPage'
import { ThreatDetectionPage } from './pages/ThreatDetectionPage'
import { ExplainableAIPage } from './pages/ExplainableAIPage'
import { ThreatIntelligencePage } from './pages/ThreatIntelligencePage'
import { AIAssistantPage } from './pages/AIAssistantPage'
import { AlertManagementPage } from './pages/AlertManagementPage'
import { ReportsPage } from './pages/ReportsPage'
import { QuantumSecurityPage } from './pages/QuantumSecurityPage'
import { SettingsPage } from './pages/SettingsPage'
import { AboutPage } from './pages/AboutPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { ErrorPage } from './pages/ErrorPage'

interface RouterContext {
  queryClient: QueryClient
}

const rootRoute = createRootRouteWithContext<RouterContext>()({
  component: () => <Outlet />,
  errorComponent: () => <ErrorPage />,
  notFoundComponent: () => <NotFoundPage />,
})

const authRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: 'auth',
  beforeLoad: () => {
    if (tokens.getAccessToken()) {
      throw redirect({ to: '/dashboard' })
    }
  },
  component: () => <Outlet />,
})

const loginRoute = createRoute({
  getParentRoute: () => authRoute,
  path: '/login',
  component: LoginPage,
})

const registerRoute = createRoute({
  getParentRoute: () => authRoute,
  path: '/register',
  component: RegisterPage,
})

const forgotPasswordRoute = createRoute({
  getParentRoute: () => authRoute,
  path: '/forgot-password',
  component: ForgotPasswordPage,
})

const resetPasswordRoute = createRoute({
  getParentRoute: () => authRoute,
  path: '/reset-password',
  component: ResetPasswordPage,
})

const appRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: 'app',
  beforeLoad: () => {
    if (!tokens.getAccessToken()) {
      throw redirect({ to: '/login' })
    }
  },
  component: AppLayout,
})

const dashboardRoute = createRoute({
  getParentRoute: () => appRoute,
  path: '/dashboard',
  component: DashboardPage,
})

const packetsRoute = createRoute({
  getParentRoute: () => appRoute,
  path: '/packets',
  component: PacketMonitoringPage,
})

const detectionRoute = createRoute({
  getParentRoute: () => appRoute,
  path: '/detection',
  component: ThreatDetectionPage,
})

const explainableAiRoute = createRoute({
  getParentRoute: () => appRoute,
  path: '/explainable-ai',
  component: ExplainableAIPage,
})

const threatIntelRoute = createRoute({
  getParentRoute: () => appRoute,
  path: '/threat-intel',
  component: ThreatIntelligencePage,
})

const assistantRoute = createRoute({
  getParentRoute: () => appRoute,
  path: '/assistant',
  component: AIAssistantPage,
  validateSearch: (search: Record<string, unknown>) => ({
    q: typeof search.q === 'string' ? search.q : undefined,
  }),
})

const alertsRoute = createRoute({
  getParentRoute: () => appRoute,
  path: '/alerts',
  component: AlertManagementPage,
})

const reportsRoute = createRoute({
  getParentRoute: () => appRoute,
  path: '/reports',
  component: ReportsPage,
})

const quantumRoute = createRoute({
  getParentRoute: () => appRoute,
  path: '/quantum',
  component: QuantumSecurityPage,
})

const settingsRoute = createRoute({
  getParentRoute: () => appRoute,
  path: '/settings',
  component: SettingsPage,
})

const aboutRoute = createRoute({
  getParentRoute: () => appRoute,
  path: '/about',
  component: AboutPage,
})

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  beforeLoad: () => {
    if (tokens.getAccessToken()) {
      throw redirect({ to: '/dashboard' })
    }
    throw redirect({ to: '/login' })
  },
  component: () => null,
})

export const routeTree = rootRoute.addChildren([
  indexRoute,
  authRoute.addChildren([loginRoute, registerRoute, forgotPasswordRoute, resetPasswordRoute]),
  appRoute.addChildren([
    dashboardRoute,
    packetsRoute,
    detectionRoute,
    explainableAiRoute,
    threatIntelRoute,
    assistantRoute,
    alertsRoute,
    reportsRoute,
    quantumRoute,
    settingsRoute,
    aboutRoute,
  ]),
])
