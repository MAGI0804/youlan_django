package utils

import (
	"crypto/rand"
	"encoding/base64"
	"fmt"
	"time"
	"django_to_go/config"
	"github.com/golang-jwt/jwt/v4"
)

// GenerateTokens 生成访问令牌和刷新令牌
func GenerateTokens(userID int, cfg config.Config) (string, string, error) {
	// 生成访问令牌
	expirationTime := time.Now().Add(time.Duration(cfg.JWTConfig.AccessTokenTTL) * time.Hour)
	claims := &jwt.RegisteredClaims{
		ExpiresAt: jwt.NewNumericDate(expirationTime),
		IssuedAt:  jwt.NewNumericDate(time.Now()),
		NotBefore: jwt.NewNumericDate(time.Now()),
		Subject:   fmt.Sprintf("%d", userID),
	}

	accessToken := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	signedAccessToken, err := accessToken.SignedString([]byte(cfg.JWTConfig.SecretKey))
	if err != nil {
		return "", "", err
	}

	// 生成刷新令牌
	refreshExpirationTime := time.Now().Add(time.Duration(cfg.JWTConfig.RefreshTokenTTL) * time.Hour)
	refreshClaims := &jwt.RegisteredClaims{
		ExpiresAt: jwt.NewNumericDate(refreshExpirationTime),
		IssuedAt:  jwt.NewNumericDate(time.Now()),
		NotBefore: jwt.NewNumericDate(time.Now()),
		Subject:   fmt.Sprintf("%d", userID),
	}

	refreshToken := jwt.NewWithClaims(jwt.SigningMethodHS256, refreshClaims)
	signedRefreshToken, err := refreshToken.SignedString([]byte(cfg.JWTConfig.SecretKey))
	if err != nil {
		return "", "", err
	}

	return signedAccessToken, signedRefreshToken, nil
}

// ParseToken 解析JWT令牌
func ParseToken(tokenString string, cfg config.Config) (*jwt.Token, error) {
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		// 验证签名算法
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return []byte(cfg.JWTConfig.SecretKey), nil
	})

	return token, err
}

// RefreshToken 刷新访问令牌
func RefreshToken(refreshTokenString string, cfg config.Config) (string, string, error) {
	token, err := ParseToken(refreshTokenString, cfg)
	if err != nil {
		return "", "", err
	}

	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok || !token.Valid {
		return "", "", fmt.Errorf("invalid refresh token")
	}

	// 获取用户ID
	userIDStr, ok := claims["sub"].(string)
	if !ok {
		return "", "", fmt.Errorf("invalid user ID in token")
	}

	var userID int
	fmt.Sscanf(userIDStr, "%d", &userID)

	// 生成新的访问令牌和刷新令牌
	return GenerateTokens(userID, cfg)
}

// GenerateUniqueFilename 生成唯一的文件名
func GenerateUniqueFilename(originalFilename string) string {
	timestamp := time.Now().UnixNano()
	randomBytes := make([]byte, 8)
	_, err := rand.Read(randomBytes)
	if err != nil {
		// 如果生成随机数失败，只使用时间戳
		return fmt.Sprintf("%d_%s", timestamp, originalFilename)
	}

	randomStr := base64.URLEncoding.EncodeToString(randomBytes)
	// 移除base64中的特殊字符
	randomStr = removeSpecialChars(randomStr)

	return fmt.Sprintf("%d_%s_%s", timestamp, randomStr, originalFilename)
}

// removeSpecialChars 移除字符串中的特殊字符
func removeSpecialChars(s string) string {
	result := ""
	for _, char := range s {
		if (char >= 'a' && char <= 'z') || (char >= 'A' && char <= 'Z') || (char >= '0' && char <= '9') {
			result += string(char)
		}
	}
	return result
}

// IsValidPhone 验证手机号格式是否正确
func IsValidPhone(phone string) bool {
	// 简单验证：11位数字，以1开头
	if len(phone) != 11 {
		return false
	}

	for i, char := range phone {
		if i == 0 && char != '1' {
			return false
		}
		if char < '0' || char > '9' {
			return false
		}
	}

	return true
}

// FormatDateTime 格式化时间
func FormatDateTime(t time.Time) string {
	return t.Format("2006-01-02 15:04:05")
}

// ParseDateTime 解析时间字符串
func ParseDateTime(datetimeStr string) (time.Time, error) {
	return time.Parse("2006-01-02 15:04:05", datetimeStr)
}

// Pagination 分页辅助函数
func Pagination(pageNum, pageSize int) (int, int) {
	if pageNum <= 0 {
		pageNum = 1
	}
	if pageSize <= 0 {
		pageSize = 10
	}
	offset := (pageNum - 1) * pageSize
	return offset, pageSize
}