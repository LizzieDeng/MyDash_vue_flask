// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import axios from 'axios'
import UUID from 'vue-uuid'
import VueCookies from 'vue-cookies'

Vue.use(UUID)
Vue.use(ElementUI)
// Vue.use(Plotly)
Vue.config.productionTip = false
Vue.prototype.$ajax = axios
Vue.use(VueCookies)
export const eventBus = new Vue()
// Vue.prototype.$eventBus = new Vue()
/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
