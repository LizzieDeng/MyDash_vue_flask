<template>
    <el-form :model="loginForm" status-icon :rules="rules" ref="loginForm" label-width="100px">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="loginForm.username" placeholder="请输入用户名"></el-input>
          <div class="user">
            <img src="../assets/user_pic.png" alt="">
          </div>
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input type="password" v-model="loginForm.password" placeholder="请输入您的密码" autocomplete="off"></el-input>
         <div class="lock">
            <img src="../assets/lock.png" alt="">
          </div>
      </el-form-item>
      <p class="item" @click="clearCookie">忘记密码？</p>
      <el-checkbox v-model="checkedUser">记住用户名</el-checkbox>
      <el-form-item>
        <el-button type="primary" @click="submitForm('loginForm')" class="submit_btn">登录</el-button>
         <el-button @click="resetForm('loginForm')">重置</el-button>
      </el-form-item>
</el-form>
</template>
<script>
export default {
  data () {
    var checkUser = (rule, value, callback) => {
      console.log('checkUser rule:', rule)
      if (!value) {
        return callback(new Error('用户名不能为空'))
      }
      // setTimeout(() => {
      //   if (!Number.isInteger(value)) {
      //     callback(new Error('请输入数字值'))
      //   } else {
      //     if (value < 18) {
      //       callback(new Error('必须年满18岁'))
      //     } else {
      //       callback()
      //     }
      //   }
      // }, 1000)
    }
    var validatePass = (rule, value, callback) => {
      console.log('validatePass rule:', rule)
      if (value === '') {
        callback(new Error('请输入密码'))
      } else {
        if (this.loginForm.password !== '') {
          this.$refs.loginForm.validateField('password')
        }
        callback()
      }
    }
    // var validatePass2 = (rule, value, callback) => {
    //   if (value === '') {
    //     callback(new Error('请再次输入密码'))
    //   } else if (value !== this.ruleForm.pass) {
    //     callback(new Error('两次输入密码不一致!'))
    //   } else {
    //     callback()
    //   }
    // }
    return {
      loginForm: {
        username: '',
        password: ''
        // age: ''
      },
      rules: {
        pass: [
          { validator: validatePass, trigger: 'blur' }
        ],
        // checkPass: [
        //   { validator: validatePass2, trigger: 'blur' }
        // ],
        age: [
          { validator: checkUser, trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    submitForm (formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          alert('submit!')
        } else {
          console.log('error submit!!')
          return false
        }
      })
    },
    resetForm (formName) {
      this.$refs[formName].resetFields()
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
