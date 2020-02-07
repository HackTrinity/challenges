package com.lololol.jason.util.convert;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.lololol.jason.util.Command;

public class Image extends Command {
    public enum Format {
        PNG("png", "image/png"),
        JPEG("jpeg", "image/jpeg"),
        GIF("gif", "image/gif"),
        TIFF("tiff", "image/tiff");

        private final String magickFormat, mimeType;
        Format(String format, String mime) {
            this.magickFormat = format;
            this.mimeType = mime;
        }

        public String getMagickFormat() {
            return magickFormat;
        }
        public String getMimeType() {
            return mimeType;
        }
    }

    @JsonCreator
    protected Image(@JsonProperty("inFormat") Format inFormat, @JsonProperty("inData") byte[] inData,
                    @JsonProperty("outFormat") Format outFormat) {
        super.setExe("convert");
        super.addArg(inFormat.getMagickFormat()+":-");
        super.addArg(outFormat.getMagickFormat()+":-");

        super.setInput(inData);
        super.setOutputType(outFormat.getMimeType());
    }

    @Override
    public void setExe(String exe) {
        throw new IllegalArgumentException("ImageMagick command cannot be modified");
    }
    @Override
    public void addArg(String arg) {
        throw new IllegalArgumentException("ImageMagick command cannot be modified");
    }
    @Override
    public void setInput(byte[] data) {
        throw new IllegalArgumentException("ImageMagick command cannot be modified");
    }
}
