package httpserver

import (
	"e2mgr/controllers"
	"e2mgr/logger"
	"e2mgr/middleware"
	"fmt"
	"net/http"
	"time"

	"github.com/gorilla/mux"
)

func Run(log *logger.Logger, port int, rootController controllers.IRootController, nodebController controllers.INodebController, e2tController controllers.IE2TController, symptomdataController controllers.ISymptomdataController) error {
	router := mux.NewRouter()

	rateLimiter := middleware.NewRateLimiter(log, 10.0, 20)
	router.Use(rateLimiter.Middleware)
	router.Use(middleware.TimeoutMiddleware(30 * time.Second))

	initializeRoutes(router, rootController, nodebController, e2tController, symptomdataController)

	addr := fmt.Sprintf(":%d", port)
	err := http.ListenAndServe(addr, router)
	log.Errorf("#http_server.Run - Fail initiating HTTP server. Error: %v", err)
	return err
}
