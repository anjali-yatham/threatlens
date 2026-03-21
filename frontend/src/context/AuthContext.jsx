import { createContext, useState, useContext, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function verify() {
      const token = localStorage.getItem('token')
      if (token) {
        try {
          const res = await axios.get('http://localhost:5000/api/auth/verify', {
            headers: { Authorization: `Bearer ${token}` }
          })
          setUser(res.data)
        } catch {
          localStorage.removeItem('token')
          setUser(null)
        }
      }
      setLoading(false)
    }
    verify()
  }, [])

  const login = async (email, password) => {
    const res = await axios.post('http://localhost:5000/api/auth/login', { email, password })
    localStorage.setItem('token', res.data.token)
    setUser({ name: res.data.name, email: res.data.email })
    return res.data
  }

  const signup = async (name, email, password) => {
    const res = await axios.post('http://localhost:5000/api/auth/signup', { name, email, password })
    localStorage.setItem('token', res.data.token)
    setUser({ name: res.data.name, email: res.data.email })
    return res.data
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}