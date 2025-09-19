package middleware

import (
	"django_to_go/config"
	"django_to_go/utils"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v4"
)

// JWTAuthMiddleware JWT认证中间件
func JWTAuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		var tokenString string
		
		// 尝试从Authorization头获取token
		authHeader := c.GetHeader("Authorization")
		if authHeader != "" {
			// 检查token格式
			authParts := strings.SplitN(authHeader, " ", 2)
			if len(authParts) == 2 && authParts[0] == "Bearer" {
				tokenString = authParts[1]
			}
		}
		
		// 如果Authorization头中没有有效的token，尝试从URL参数access_token获取
		if tokenString == "" {
			tokenString = c.Query("access_token")
		}
		
		// 如果两种方式都没有获取到token，返回未授权
		if tokenString == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Authorization token is required, either in header or as access_token query parameter"})
			c.Abort()
			return
		}
		// 解析token
		cfg := config.LoadConfig()
		token, err := utils.ParseToken(tokenString, cfg)
		if err != nil || !token.Valid {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid or expired token"})
			c.Abort()
			return
		}

		// 提取用户信息
		claims, ok := token.Claims.(jwt.MapClaims)
		if !ok {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token claims"})
			c.Abort()
			return
		}

		// 获取用户ID
		userIDStr, ok := claims["sub"].(string)
		if !ok {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "User ID not found in token"})
			c.Abort()
			return
		}

		// 将用户ID存储到上下文中
		c.Set("userID", userIDStr)
		c.Next()
	}
}

// CORSMiddleware 跨域中间件
func CORSMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT, DELETE")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	}
}

// RequestLogMiddleware 请求日志中间件
func RequestLogMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 记录请求信息
		// 这里可以根据需要添加日志记录逻辑
		c.Next()
	}
}

// ErrorHandlerMiddleware 错误处理中间件
func ErrorHandlerMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Next()

		// 处理错误
		if len(c.Errors) > 0 {
			for _, _ = range c.Errors {
				// 这里可以根据需要添加错误处理逻辑
				// 例如记录错误日志、返回统一的错误格式等
			}
		}
	}
}
