<template>
     <el-header>
       <h1>{{header}}</h1>
     </el-header>
</template>
<script>
export default {
  data () {
    return {
      header: '姿态路径展示'
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
/*h3{*/
/*  display: none;*/
/*}*/
</style>
