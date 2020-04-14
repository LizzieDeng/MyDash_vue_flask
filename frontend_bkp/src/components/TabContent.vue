<template>
       <el-aside>
                <div id="tabs_style">
                     <!-- tab part data source -->
                     <el-tabs type="border-card" style="height: 35vh" >
                            <el-tab-pane label="数据文件">
                                <!-- 上传文件 -->
                                <el-upload
                                  class="upload-demo"
                                  ref="upload"
                                  action="https://jsonplaceholder.typicode.com/posts/"
                                  :before-upload="beforeAvatarUpload"
                                  :on-preview="handlePreview"
                                  :on-remove="handleRemove"
                                  :on-exceed="handleExceed"
                                  :file-list="fileList"
                                  :limit="1"
                                  :multiple="false"
                                  :auto-upload="false">
                                  <el-button slot="trigger" size="small" type="primary">选取文件</el-button>
                                  <el-button style="margin-left: 10px;" size="small" type="success" @click="submitUpload">上传到服务器</el-button>
                                  <div slot="tip" class="el-upload__tip">只能上传jpg/png文件，且不超过500kb</div>
                                </el-upload>
                            </el-tab-pane>
                            <el-tab-pane label="数据流">
                                 <!-- 输入栏-->
                                <div id="file_flow">
                                    <P>请输入服务器地址:</P>
                                    <el-input/>
                                </div>
                                 <!-- 连接与断开按钮-->
                                <div id="websocket_connect_btn">
                                  <el-row>
                                      <el-button type="primary" plain>连接</el-button>
                                      <el-button type="primary" plain>断开</el-button>
                                    </el-row>
                                </div>
                            </el-tab-pane>
                     </el-tabs>
                     <br>
                      <!-- tab part data control-->
                     <el-tabs type="border-card" style="height: 60vh;">
                        <el-tab-pane label="动态">
                            <!-- 步伐 -->
                            <el-dropdown>
                                <span class="el-dropdown-link">
                                步伐<i class="el-icon-arrow-down el-icon--right"></i>
                                </span>
                                <el-dropdown-menu slot="dropdown" >
                                    <el-dropdown-item>200</el-dropdown-item>
                                    <el-dropdown-item>400</el-dropdown-item>
                                    <el-dropdown-item>800</el-dropdown-item>
                                    <el-dropdown-item>1600</el-dropdown-item>
                                    <el-dropdown-item>2000</el-dropdown-item>
                                </el-dropdown-menu>
                            </el-dropdown>
                            <el-row>
                                 <div id="draw_path_graph_btn">
                                    <el-button type="primary" plain @click.native="drawPathGraph">画路径图</el-button>
                                </div>
                            </el-row>
                        </el-tab-pane>
                        <el-tab-pane label="静态">
                             <div id="locate_nb" >
                                <p>定位:</p>
                                <el-input/>
                            </div>
                            <div id="path_step">
                               <p>步伐:</p>
                                <el-input/>
                            </div>
                            <el-row>
                                  <el-button type="primary" plain>前进</el-button>
                                  <el-button type="primary" plain>后退</el-button>
                            </el-row>
                            <el-checkbox>是否同步视角</el-checkbox>
                        </el-tab-pane>
                        <el-tab-pane label="时间">
                        </el-tab-pane>
                    </el-tabs>
                </div>
       </el-aside>
</template>
<script>
import axios from 'axios'
export default {
  data () {
    return {
      fileList: [],
      formData: ''
    }
  },
  methods: {
    handleRemove (file, fileList) {
      console.log(file, fileList)
    },
    handlePreview (file) {
      console.log(file)
    },
    handleExceed (files, fileList) {
      this.$message.warning(`最多上传 ${files.length} 个文件`)
    },
    beforeAvatarUpload (file) {
      console.log('beforeAvatarUpload')
      const iscsv = file.type === 'application/vnd.ms-excel'
      if (!iscsv) {
        this.$message.error('上传文件只能是 Excel 格式!')
      }
      this.formData.append('file', file.file)
    },
    submitUpload () {
      // this.$refs.upload.submit()
      let formData = new FormData()
      // formData.append('theme', this.theme)this.fileList[0].raw
      console.log('submit:', this.fileList)
      formData.append('file', this.fileList)
      axios({
        url: this.HOME + '/api/upload',
        method: 'post',
        data: formData,
        headers: {
          'Content-Type': 'multipart/form-data;charset=utf-8'
        }
      }).then(res => {
        if (res.data.success) {
          alert('导入成功!')
        } else {
          alert(res.data.message + ',' + res.data.data)
        }
      })
        .catch(err => {
          console.log(err)
        })
    }
  }}
</script>

<style>
.el-aside {
   width: 25vw;
}
#tabs_style {
  width: 24vw;
  float: left;
  height: 98vh;
}
.el-input, .el-button{
  margin-bottom:5px;
  margin-top:5px
}
.span{
  float: left;
  margin-top: 5px;
  margin-bottom: 5px
}
#draw_path_graph_btn,.el-dropdown{
    margin-top: 5px;
    float: left;
}
.el-checkbox {
  margin-top:5px
}
p{
  float: left;
}
</style>
