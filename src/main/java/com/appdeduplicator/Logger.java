package com.appdeduplicator;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

public class Logger {
    private final List<String> logs;
    private final String logFile;
    private final DateTimeFormatter formatter;

    public Logger() {
        this.logs = new ArrayList<>();
        this.logFile = "appdeduplicator.log";
        this.formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    }

    public void log(String message) {
        String timestamp = LocalDateTime.now().format(formatter);
        String logEntry = String.format("[%s] %s", timestamp, message);
        logs.add(logEntry);
        
        // Also write to file
        try (PrintWriter writer = new PrintWriter(new FileWriter(logFile, true))) {
            writer.println(logEntry);
        } catch (IOException e) {
            System.err.println("Failed to write to log file: " + e.getMessage());
        }
    }

    public void displayReport() {
        System.out.println("=== Log Report ===");
        if (logs.isEmpty()) {
            System.out.println("No log entries found.");
            return;
        }

        System.out.println("Total log entries: " + logs.size());
        System.out.println("\nRecent logs:");
        
        // Show last 20 entries
        int start = Math.max(0, logs.size() - 20);
        for (int i = start; i < logs.size(); i++) {
            System.out.println(logs.get(i));
        }
        
        System.out.println("\nFull log saved to: " + logFile);
    }

    public List<String> getLogs() {
        return new ArrayList<>(logs);
    }

    public void clearLogs() {
        logs.clear();
        try {
            Files.deleteIfExists(Paths.get(logFile));
        } catch (IOException e) {
            System.err.println("Failed to clear log file: " + e.getMessage());
        }
    }
}