package main

import (
	"log"
	"github.com/gin-gonic/gin"
	"github.com/youlan-kids/youlan_kids_go/django_to_go/config"
	"github.com/youlan-kids/youlan_kids_go/django_to_go/db"
	"github.com/youlan-kids/youlan_kids_go/django_to_go/middleware"
	"github.com/youlan-kids/youlan_kids_go/django_to_go/routes"
)

func main() {
	// 加载配置
	appConfig := config.LoadConfig()
	
	// 初始化数据库
	db.InitDB(appConfig)

	// 创建Gin引擎
	router := gin.Default()

	// 设置中间件
	router.Use(gin.Logger())
	router.Use(gin.Recovery())
	router.Use(middleware.CORSMiddleware())
	router.Use(middleware.RequestLogMiddleware())
	router.Use(middleware.ErrorHandlerMiddleware())

	// 设置静态文件服务
	router.Static("/static", "./staticfiles")
	router.Static("/media", "./media")

	// 初始化路由
	routes.InitRoutes(router)

	// 启动服务器
	port := "8080"
	log.Printf("Server starting on port %s\n", port)
	if err := router.Run(":" + port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}