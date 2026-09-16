FROM eclipse-temurin:11-jdk

RUN apt-get update && apt-get install -y --no-install-recommends procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Chronicle-style append-only persisted queue demo (file-backed, ultra-simple)
RUN cat > ChronicleDemo.java <<'JAVA'
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;

public class ChronicleDemo {
    public static void main(String[] args) throws Exception {
        Path dir = Paths.get("/tmp/chronicle-demo");
        Files.createDirectories(dir);
        Path queue = dir.resolve("queue.log");
        System.out.println("Starting Chronicle-style queue demo at " + queue);
        int n = 0;
        while (true) {
            n++;
            String message = "Hello from Chronicle Queue! Message #" + n + "\n";
            Files.write(queue, message.getBytes(StandardCharsets.UTF_8),
                    StandardOpenOption.CREATE, StandardOpenOption.APPEND);
            System.out.println("Sent: " + message.trim());
            Thread.sleep(5000);
        }
    }
}
JAVA

RUN javac ChronicleDemo.java

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD pgrep -f ChronicleDemo || exit 1
CMD ["java", "ChronicleDemo"]
