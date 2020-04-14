<template>
<!--    <el-container>-->
                 <el-main style="margin-left: 300px; height: 86vh;background-color: yellow">
                    <!-- path graph-->
                    <div id="path_graph_container">
                    </div>
                    <!--gesture graph-->
                    <div id="gesture_graph_container">
                    </div>
                    <!--stream graph-->
                    <div id="streaming_graph_container">
                    </div>
                 </el-main>
<!--             </el-container>-->
</template>
<script>
export default {
  data () {
    return {
      // header: '姿态路径展示'
    }
  }
}
</script>

<style scoped>
.el-container{
 width: 75vw; height: 86vh;background-color: yellow
}
</style>
