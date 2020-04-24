<template>
  <div id="app">
    <Header></Header>
    <div>
      <!-- left tabs -->
      <TabContent></TabContent>
      <!-- right graphs -->
     <pathGraph :divId="pathPlot" style="height: 800px; margin-left: 350px"></pathGraph>
       <!-- <plotlyGraph :propData="plotInfo" divId="plot_1" style="height: 300px; margin-left: 350px"></plotlyGraph> -->
    </div>
  </div>
</template>

<script>
import Header from './components/Header'
import TabContent from './components/TabContent'
import pathGraph from './components/pathGraph'
import plotlyGraph from './components/plotlyGraph'

export default {
  name: 'App',
  components: {
    // eslint-disable-next-line no-undef
    Header, TabContent, pathGraph, plotlyGraph
  },
  data: function () {
    return ({
      pathPlot: 'pathplot'
    })
  },
  mounted () {
    // this.updatePlot()
  },
  methods: {
    // updatePlot () {
    //   let x = []
    //   let y = []
    //   for (let i = -5; i <= 5; i += 0.01) {
    //     x.push(i)
    //     if (this.selectedFunction === 0) {
    //       y.push(this.A * Math.sin(this.B * i))
    //     } else if (this.selectedFunction === 1) {
    //       y.push(this.A * Math.cos(this.B * i))
    //     } else if (this.selectedFunction === 2) {
    //       y.push(this.A * Math.pow(this.B, i))
    //     } else {
    //       // BigEval takes a string representing an equation, and evaluates it. It returns an ERROR if the syntax is invalid
    //       let cmd = this.equation.replace(/y/g, '').replace(/ /g, '').replace(/=/g, '').replace(/A/g, this.A.toString()).replace(/B/g, this.B.toString()).replace(/x/g, i.toString())
    //       let res = this.eq.exec(cmd)
    //       y.push(res)
    //     }
    //   }
    //   let data = [{
    //     x: x,
    //     y: y,
    //     type: 'scatter',
    //     line: {
    //       width: 4
    //     }
    //   }]
    //   let layout = {
    //     // get rid of all the extra whitespace around plots
    //     margin: {
    //       t: 25,
    //       b: 25,
    //       r: 25,
    //       l: 25
    //     },
    //     paper_bgcolor: '#ECEFF1'
    //   }
    //   let config = {
    //     // newish in plotly...auto-resizes on window resize
    //     responsive: true
    //   }
    //   this.plotInfo = { data: data, layout: layout, config: config }
    // }
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
