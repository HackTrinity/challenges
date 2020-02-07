package com.lololol.jason.util;

import com.fasterxml.jackson.annotation.JsonProperty;

public class CommandResult {
    private final String mimeType;
    private final byte[] data;

    public CommandResult(String mimeType, byte[] data) {
        this.mimeType = mimeType;
        this.data = data;
    }

    @JsonProperty
    public String getMimeType() {
        return mimeType;
    }
    @JsonProperty
    public byte[] getData() {
        return data;
    }
}
