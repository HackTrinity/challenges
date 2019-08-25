package com.lololol.jason.util.convert;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.lololol.jason.util.Command;

public class YamlJson extends Command {
    public enum Format {
        JSON("application/json"), YAML("application/x-yaml");

        private final String mimeType;
        Format(String mime) {
            this.mimeType = mime;
        }

        public String getMimeType() {
            return mimeType;
        }
    }

    @JsonCreator
    protected YamlJson(@JsonProperty("inData") byte[] inData, @JsonProperty("outFormat") Format outFormat) {
        super.setExe("yq");
        super.addArg("read");
        super.addArg("-");

        if (outFormat == Format.JSON) {
            super.addArg("--tojson");
        }

        super.setInput(inData);
        super.setOutputType(outFormat.getMimeType());
    }

    @Override
    public void setExe(String exe) {
        throw new IllegalArgumentException("YamlJsonConvert command cannot be modified");
    }
    @Override
    public void addArg(String arg) {
        throw new IllegalArgumentException("YamlJsonConvert command cannot be modified");
    }
    @Override
    public void setInput(byte[] data) {
        throw new IllegalArgumentException("YamlJsonConvert command cannot be modified");
    }
}
