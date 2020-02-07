package com.lololol.jason;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;

import io.reactivex.Completable;
import io.vertx.core.http.HttpServerOptions;
import io.vertx.core.json.Json;
import io.vertx.reactivex.core.AbstractVerticle;
import io.vertx.reactivex.core.buffer.Buffer;
import io.vertx.reactivex.ext.web.Router;
import io.vertx.reactivex.ext.web.RoutingContext;
import io.vertx.reactivex.ext.web.handler.BodyHandler;
import io.vertx.reactivex.ext.web.handler.LoggerHandler;
import io.vertx.reactivex.ext.web.handler.StaticHandler;

import com.lololol.jason.util.Command;

public class AppVerticle extends AbstractVerticle {
    public long MAX_BODY_SIZE = 8 * 1024 * 1024;

    public class Error {
        private Throwable ex;
        public Error(Throwable ex) {
            this.ex = ex;
        }

        @JsonProperty
        public String getType() {
            return ex.getClass().getSimpleName();
        }
        @JsonProperty
        public String getMessage() {
            return ex.getMessage();
        }
    }
    private void errorHandler(RoutingContext rc) {
        rc.response()
            .setStatusCode(500)
            .putHeader("Content-Type", "application/json")
            .end(Buffer.newInstance(Json.encodeToBuffer(new Error(rc.failure()))));
    }
    private void convertHandler(RoutingContext rc) {
        try {
            rc
                .getBodyAsJson()
                .mapTo(Command.class)
                .run(vertx)
                .subscribe((r, e) -> {
                    if (e != null) {
                        e.printStackTrace();
                        rc.fail(e);
                        return;
                    }

                    rc.response()
                        .end(Buffer.newInstance(Json.encodeToBuffer(r)));
                });
        } catch (RuntimeException ex) {
            rc.fail(ex);
        }
    }
    private static void configureMapper(ObjectMapper mapper) {
        mapper
            .disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES)
            .enable(DeserializationFeature.FAIL_ON_MISSING_CREATOR_PROPERTIES)
            .enable(SerializationFeature.WRAP_EXCEPTIONS);
    }
    @Override
    public Completable rxStart() {
        configureMapper(Json.mapper);
        configureMapper(Json.prettyMapper);

        Router router = Router.router(vertx);
        router.errorHandler(500, this::errorHandler);
        router.route().handler(LoggerHandler.create());
        router.post().handler(BodyHandler
            .create(false)
            .setBodyLimit(MAX_BODY_SIZE)
        );
        router
            .post("/api/convert")
            .consumes("application/json")
            .handler(this::convertHandler)
            .produces("application/json");
        router.route("/*").handler(StaticHandler.create());

        return vertx
            .createHttpServer(new HttpServerOptions().setLogActivity(true))
            .requestHandler(router)
            .rxListen(8080)
            .ignoreElement();
    }
}
