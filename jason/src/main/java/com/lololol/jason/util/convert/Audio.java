package com.lololol.jason.util.convert;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.lololol.jason.util.Command;

public class Audio extends Command {
    public enum Format {
        WAV("wav", "pcm_s16le", "audio/wav"),
        MP3("mp3", "libmp3lame", "audio/mp3"),
        VORBIS("ogg", "libvorbis", "audio/ogg"),
        OPUS("ogg", "libopus", "audio/ogg");

        private final String in, out, outputType;
        Format(String in, String out, String mime) {
            this.in = in;
            this.out = out;
            this.outputType = mime;
        }

        public String getContainer() {
            return in;
        }
        public String getEncoder() {
            return out;
        }
        public String getOutputType() {
            return outputType;
        }
    }

    @JsonCreator
    protected Audio(@JsonProperty("inFormat") Format inFormat, @JsonProperty("inData") byte[] inData,
                    @JsonProperty("outFormat") Format outFormat) {
        super.setExe("ffmpeg");

        super.addArg("-f");
        super.addArg(inFormat.getContainer());
        super.addArg("-i");
        super.addArg("-");

        super.addArg("-f");
        super.addArg(outFormat.getContainer());
        super.addArg("-c:a");
        super.addArg(outFormat.getEncoder());
        super.addArg("-");

        super.setInput(inData);
        super.setOutputType(outFormat.getOutputType());
    }

    @Override
    public void setExe(String exe) {
        throw new IllegalArgumentException("AudioConvert command cannot be modified");
    }
    @Override
    public void addArg(String arg) {
        throw new IllegalArgumentException("AudioConvert command cannot be modified");
    }
    @Override
    public void setInput(byte[] data) {
        throw new IllegalArgumentException("AudioConvert command cannot be modified");
    }
}
