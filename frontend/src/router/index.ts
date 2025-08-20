import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Incidents from '../views/Incidents.vue'
import Simulation from '../views/Simulation.vue'
import IncidentDetail from '../views/IncidentDetail.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: Dashboard,
      meta: {
        title: 'Dashboard - DevOps Crisis Commander'
      }
    },
    {
      path: '/incidents',
      name: 'incidents',
      component: Incidents,
      meta: {
        title: 'Incidents - DevOps Crisis Commander'
      }
    },
    {
      path: '/incidents/:id',
      name: 'incident-detail',
      component: IncidentDetail,
      props: true,
      meta: {
        title: 'Incident Detail - DevOps Crisis Commander'
      }
    },
    {
      path: '/simulation',
      name: 'simulation',
      component: Simulation,
      meta: {
        title: 'Simulation - DevOps Crisis Commander'
      }
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

// Update document title based on route
router.beforeEach((to, from, next) => {
  document.title = to.meta.title as string || 'DevOps Crisis Commander'
  next()
})

export default router
