<template>
    <div
    class="pathgraph"
    ref="container"
    :id='divId'
    :style="{
      height: (height) +  '%',
      width: (width) + '%'
    }"/>
</template>
<script>
import Plotly from 'plotly.js/dist/plotly'
import event from '../event'
import axios from 'axios'
export default {
  props: {
    divId: {
      type: String,
      required: true
    },
    height: {
      type: Number,
      default: 100
    },
    width: {
      type: Number,
      default: 95
    }
  },
  data () {
    return {
      // header: '姿态路径展示'
      data: '',
      pathData: ''
    }
  },
  mounted () {
    // let trace1 = [{
    //   x: [0, 1, 2, 3],
    //   y: [4, 1, 2, 1],
    //   z: [1, 6, 8, 0],
    //   mode: 'markers + lines',
    //   type: 'scatter3d'
    // }]
    // let layout = {margin: {
    //   l: 0,
    //   r: 0,
    //   b: 0,
    //   t: 0
    // }}
    // // eslint-disable-next-line no-undef
    // Plotly.newPlot('path_graph_container', trace1, layout)
  },
  created () {
    event.$on('drawPath', function (param) {
      console.log('param', param)
      let uuid = param
      // 通过uuid请求后端path数据
      axios.post('http://127.0.0.1:5000/api/getpath',
        {
          'uuid': uuid
        })
        .then(res => {
          if (res.data.success) {
            this.pathData = res.data.data
            alert('后台数据返成功!')
            console.log('before this data', this.pathData)
            this.data = [{
              x: this.pathData.x,
              y: this.pathData.y,
              z: this.pathData.z,
              type: 'scatter3d',
              mode: 'markers'
            }]
            // this.data = [{ x: [0],
            //   y: [0],
            //   z: [0],
            //   name: '动画',
            //   type: 'scatter3d',
            //   mode: 'markers',
            //   marker: {size: 0},
            //   opacity: 0
            // }, {
            //   x: [30, 50, 20, 60, 44, 88, 98, 22],
            //   y: [30, 50, 20, 60, 44, 88, 70, 22],
            //   z: [30, 50, 20, 10, 44, 19, 9, 22],
            //   type: 'scatter3d',
            //   mode: 'markers',
            //   showlegend: false
            // }]
            let layout = {
              autosize: true,
              height: 880,
              width: 800,
              // get rid of all the extra whitespace around plots
              margin: {
                t: 25,
                b: 25,
                r: 25,
                l: 25
              }
              // paper_bgcolor: '#ECEFF1'
            }
            let config = {
              // newish in plotly...auto-resizes on window resize
              responsive: true
            }
            console.log('this.divId', this.divId, this.data)
            Plotly.newPlot('pathplot', this.data, layout, config)
            // this.newPlotly()
          } else {
            alert(res.data.message + ',' + res.data.data)
          }
        }).catch(function (error) {
          console.log('get path', error)
        })
    })
  },
  methods: {
    newPlotly () {
      let layout = {
        autosize: true,
        height: 880,
        // get rid of all the extra whitespace around plots
        margin: {
          t: 25,
          b: 25,
          r: 25,
          l: 25
        },
        paper_bgcolor: '#ECEFF1'
      }
      let config = {
        // newish in plotly...auto-resizes on window resize
        responsive: true
      }
      Plotly.newPlot(this.divId, this.data, layout, config)
    }
  }

}
</script>

<style scoped>
.el-container{
 width: 75vw; height: 86vh;background-color: yellow
}
</style>
