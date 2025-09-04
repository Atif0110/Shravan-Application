import { ref, computed } from 'vue'
import { defineStore } from 'pinia'


export const auth = defineStore('auth',()=>{
    const backend_url = 'http://127.0.0.1:5000'
    const token = ref(localStorage.getItem('token'))
    const user_details = ref(localStorage.getItem('user_details'))
    const username = computed(()=>JSON.parse(user_details.value).username)
    const email = computed(()=> JSON.parse(user_details.value).email)
    //const role = computed(()=>JSON.parse(user_details.value).role)
    var role

    const isAuthenticated = computed(()=>token.value !== null)

    function updateToken(){
        token.value = localStorage.getItem('token')
    }

    function updateUser(){
        user_details.value = localStorage.getItem('user_details')
    }

    function setToken(token){
        localStorage.setItem('token',token)
    }

    function removeToken(){
        localStorage.removeItem('token')
        token.value = null
    }

    function removeUserDetails(){
        localStorage.removeItem('user_details')
        localStorage.removeItem('userName')
        user_details.value = null
    }

    function setUserDetails(user_dets){
        localStorage.setItem('user_details',user_dets)
    }
    
    async function logout(){
        try{
            const response = await fetch(`${backend_url}/api/users/logout`,{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Authentication-Token': token.value
                }
            })
            if (!response.ok){
                const data = await response.json()
                const rsp = {
                    'status': false,
                    'message': data.error
                }
                console.log(rsp);
                return rsp
            }
            else{
                const data = await response.json()
                const rsp = {
                    'status': true,
                    'message': data.message
                }
                console.log("Logout Successfull", role)
                removeToken()
                removeUserDetails()
                updateToken()
                updateUser()
                return rsp
            }
        }
        catch(error){
            console.error(error)
            const rsp = {
                'status': false,
                'message': 'Oops! Something Went Wrong'
            }
            return rsp
        }
    }

    async function login(user_details){
        try{
            const response = await fetch(`${backend_url}/api/users/login`,{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                body: JSON.stringify(user_details)
            })
            console.log(response);
            if (!response.ok){
                const data = await response.json()
                const rsp = {
                    'status': false,
                    'message': data.error
                }
                return rsp
            }
            else{
                const data = await response.json()
                console.log(data);
                // if (data.user.auth_token){
                //     setToken(data.user.auth_token)
                //     const user_dets = {
                //         'username':data.user.user_name,
                //         'role':data.user.role,
                //         'email':data.user.email,
                //     }
                //     console.log(user_dets);
                //     setUserDetails(JSON.stringify(user_dets))
                //     const rsp = {
                //         'status': true,
                //         'message': data.message
                //     }
                //     console.log(rsp);
                //     updateToken()
                //     updateUser()
                //     return rsp
                //}
                const user_dets = {
                    'user_id':data.user.user_id,
                    'username':data.user.user_name,
                    'role':data.user.role,
                    'email':data.user.email,
                }
                role = data.user.role;

                setUserDetails(JSON.stringify(user_dets))
                localStorage.setItem('userName', data.user.user_name);

                const rsp = {
                    'status': true,
                    'message': data.message,
                    'username': data.user.user_name,
                    'role': data.user.role
                }
                return rsp
            }
        }
        catch(error){
            console.error(error)
            const rsp = {
                'status': true,
                'message': 'Oops! Something Went Wrong'
            }
            return rsp
        }
    }

    async function register(user_details){
        try{
            const response = await fetch(`${backend_url}/api/create_user`,{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                body: JSON.stringify(user_details)
            })
            if (!response.ok){
                const data = await response.json()
                const rsp = {
                    'status': false,
                    'message': data.error
                }
                return rsp
            }
            else{
                const data = await response.json()
                const rsp = {
                    'status': true,
                    'message': data.message
                    
                }
                return rsp
            }
        }
        catch(error){
            console.error(error)
            const rsp = {
                'status': false,
                'message': 'Oops! Something Went Wrong'
            }
            return rsp
        }
    }


    return {login, logout, register ,token, username, isAuthenticated, backend_url, role,email, updateUser}
});