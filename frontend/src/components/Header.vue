<template>
     <el-header>
       <h1>{{header}}</h1>
       <h3 class="'uuid">{{uuid}}</h3>
     </el-header>
</template>
<script>
import {uuid} from 'vue-uuid'
import {eventBus} from '../main'

export default {
  data () {
    return {
      header: '姿态路径展示',
      uuid: uuid.v1()
    }
  },
  methods: {
    created: function () {
      eventBus.$emit('uuid', this.uuid)
    }
  }
}
</script>

<style scoped>
/*.el-header{*/
/*  margin: auto;*/
/*  !*height: 30px;*!*/
/*}*/
h1{
  height: 15px;
  text-align:center;
  font-size:30px
}
h3{
  display: none;
}
</style>
