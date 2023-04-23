new Vue({
  el: '#vue',
  mixins: [windowMixin],
  data: function () {
    return {
      disclaimerDialog: {
        show: false,
        data: {}
      },
      username: '',
      password: '',
      password_repeat: '',
      walletName: ''
    }
  },
  methods: {
    register: function () {
      axios({
        method: 'POST',
        url: '/api/v1/register',
        data: {
          email: this.username,
          password: this.password,
          password_repeat: this.password_repeat
        }
      })
        .then(response => {
          this.$q.localStorage.set('lnbits.token', response.token)
          this.$q.localStorage.set('lnbits.usr', response.usr)
          window.location.href = '/wallet'
        })
        .catch(LNbits.utils.notifyApiError)
    },
    login: function () {
      axios({
        method: 'POST',
        url: '/api/v1/login',
        data: {username: this.username, password: this.password}
      })
        .then(response => {
          this.$q.localStorage.set('lnbits.token', response.token)
          this.$q.localStorage.set('lnbits.usr', response.token)
          window.location.href = '/wallet'
        })
        .catch(LNbits.utils.notifyApiError)
    },
    createWallet: function () {
      LNbits.href.createWallet(this.walletName)
    },
    processing: function () {
      this.$q.notify({
        timeout: 0,
        message: 'Processing...',
        icon: null
      })
    }
  }
})
