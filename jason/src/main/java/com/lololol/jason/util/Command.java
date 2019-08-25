package com.lololol.jason.util;

import com.fasterxml.jackson.annotation.JsonTypeInfo;

import io.reactivex.Single;
import io.vertx.core.logging.Logger;
import io.vertx.core.logging.LoggerFactory;
import io.vertx.reactivex.core.Vertx;

import java.io.IOException;
import java.io.OutputStream;

@JsonTypeInfo(use = JsonTypeInfo.Id.MINIMAL_CLASS, property = "mode")
public class Command {
    private final Logger logger = LoggerFactory.getLogger(getClass());

    private String outputType = "text/plain";
    private String command;
    private byte[] inputData;

    public void setExe(String exe) {
        command = exe;
    }
    public void addArg(String argument) {
        command += " " + argument;
    }
    public void setInput(byte[] data) {
        this.inputData = data;
    }
    public void setOutputType(String mimeType) {
        this.outputType = mimeType;
    }

    public class CommandException extends RuntimeException {
        private final int status;
        private final String output;
        public CommandException(int status, byte[] output) {
            this.status = status;
            this.output = output == null ? "<none>" : new String(output);
        }

        public String getMessage() {
            return "command '" +
                command +
                "' exited with non-zero status " +
                status +
                ".\nstderr:\n" +
                output;
        }
    }
    public Single<CommandResult> run(Vertx vertx) {
        return Single
            .fromCallable(() -> Runtime.getRuntime().exec(command))
            .flatMapMaybe(proc -> vertx.rxExecuteBlocking(p -> {
                try {
                    logger.info("executing command '{}'", command);
                    if (inputData != null) {
                        try {
                            OutputStream stdin = proc.getOutputStream();
                            stdin.write(inputData);
                            stdin.close();
                        } catch (IOException e) {
                            logger.warn("failed to write input data for command '{}'", command);
                        }
                    }

                    byte[] output = proc.getInputStream().readAllBytes();
                    if (proc.waitFor() != 0) {
                        byte[] stderr = proc.getErrorStream().readAllBytes();
                        throw new CommandException(proc.exitValue(), stderr);
                    }

                    p.complete(new CommandResult(outputType, output));
                    logger.info("command '{}' done", command);
                } catch (Exception e) {
                    p.fail(e);
                }
            }))
            .toSingle()
            .map(o -> (CommandResult) o);
    }
}
