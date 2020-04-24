<template>
   <!--  left tabs -->
   <div id="tabs_style">
                   <h3 class="'uuid">{{uuid}}</h3>
                   <!-- tab part data source -->
                   <el-tabs type="border-card" style="height: 35vh; width: 300px" >
                          <el-tab-pane label="数据文件">
                              <!-- 上传文件 -->
                              <el-upload
                                class="upload-demo"
                                ref="upload"
                                action=""
                                :before-upload="beforeAvatarUpload"
                                :on-preview="handlePreview"
                                :on-remove="handleRemove"
                                :on-exceed="handleExceed"
                                :on-success="handleSuccess"
                                :http-request="uploadFile"
                                :file-list="fileList"
                                :limit="1"
                                :multiple="false"
                                :auto-upload="false">
                                <el-button slot="trigger" size="small" type="primary" plain>选取文件</el-button>
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
                   <el-tabs type="border-card" style="height: 60vh; width: 300px">
                      <el-tab-pane label="动态">
                          <!-- 步伐 -->
                        <el-row>
                              <span>步伐:</span>
                              <el-select v-model="value" placeholder="请选择" @change="selectStepGet">
                                <el-option
                                  v-for="item in options"
                                  :key="item.value"
                                  :label="item.label"
                                  :value="item.value">
                                </el-option>
                              </el-select>
                        </el-row>
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
</template>
<script>
import axios from 'axios'
import {uuid} from 'vue-uuid'
import event from '../event'

export default {
  data () {
    return {
      fileList: [],
      options: [],
      value: '',
      uuid: uuid.v1(),
      step: ''
    }
  },
  methods: {
    handleRemove (file, fileList) {
      console.log(file, fileList)
    },
    handleSuccess (response, file, fileList) {
      this.$message({
        showClose: true,
        message: '文件上传成功',
        type: 'success'
      })
    },
    uploadFile (file) {
      let formData = new FormData()
      console.log('file:', file)
      console.log('submit:', file.file)
      formData.append('file', file.file)
      formData.append('uuid', this.uuid)
      axios({
        url: 'http://127.0.0.1:5000/api/upload',
        method: 'post',
        data: formData,
        headers: {
          'Content-Type': 'multipart/form-data;charset=utf-8'
        }
      }).then(res => {
        if (res.data.success) {
          alert('导入成功!')
          this.getOptions(this.uuid)
          // eventBus.on('uuid', (message) => {
          //   this.fromuuid = message
          //   console.log('fromuuid:', message)
          //   this.getOptions(this.fromuuid)
          // })
        } else {
          alert(res.data.message + ',' + res.data.data)
        }
      })
        .catch(err => {
          console.log(err)
        }
        )
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
    },
    submitUpload (file) {
      this.$refs.upload.submit()
    },
    getOptions (uuid) {
      axios.post('http://127.0.0.1:5000/api/getopt',
        {
          'uuid': uuid
        })
        .then(response => (
          this.options = response.data.options
        ))
      // eslint-disable-next-line handle-callback-err
        .catch(function (error) {
          console.log(error)
        })
    },
    // 获取选中步伐
    selectStepGet (step) {
      let obj = this.options.find((item) => {
        if (item.value === step) {
          this.step = step
        }
        return item.value === step
      })
      console.log('obj', obj.value, this.step)
    },
    // 画路径图
    drawPathGraph () {
      event.$emit('drawPath', this.uuid)
    }
  }}
</script>

<style>
#tabs_style {
  float: left;
  height: 98vh;
}
.el-input, .el-button,.el-row{
  margin-bottom:5px;
  margin-top:5px
}
h3{
  display: none;
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
