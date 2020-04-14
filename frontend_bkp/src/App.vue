<template>
  <div id="app">
    <!--<img src="./assets/logo.png">-->
    <!--<router-view/>-->
    <Header></Header>
    <TabContent></TabContent>
  </div>
</template>

<script>

import Header from './components/Header'
import TabContent from './components/TabContent'
export default {
  name: 'App',
  components: {
    Header, TabContent
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
