package com.appdeduplicator;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.stream.Stream;

public class FileScanner {
    private final ConfigManager configManager;
    private final Logger logger;
    private final List<File> scannedFiles;
    private static final Set<String> VALID_EXTENSIONS = Set.of(".exe", ".msi", ".jar", ".apk", ".dmg", ".app", ".deb", ".rpm", ".pdf", ".txt", ".zip", ".tar", ".gz", ".7z", ".rar"," .doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx");

    public FileScanner(ConfigManager configManager, Logger logger) {
        this.configManager = configManager;
        this.logger = logger;
        this.scannedFiles = new ArrayList<>();
    }

    public void scanDirectory() throws IOException {
        String scanDir = configManager.getScanDirectory();
        Path scanPath = Paths.get(scanDir);
        
        logger.log("Starting scan of directory: " + scanDir);
        
        if (!Files.exists(scanPath)) {
            throw new IOException("Scan directory does not exist: " + scanDir);
        }
        
        if (!Files.isDirectory(scanPath)) {
            throw new IOException("Scan path is not a directory: " + scanDir);
        }
        
        scannedFiles.clear();
        
        try (Stream<Path> paths = Files.walk(scanPath)) {
            paths.filter(Files::isRegularFile)
                 .filter(this::isValidApplicationFile)
                 .map(Path::toFile)
                 .forEach(file -> {
                     scannedFiles.add(file);
                     logger.log("Found application file: " + file.getName());
                 });
        }
        
        logger.log("Scan completed. Found " + scannedFiles.size() + " application files");
    }

    public void scanCustomDirectory(String customDirectory) throws IOException {
        Path scanPath = Paths.get(customDirectory);
        
        logger.log("Starting scan of custom directory: " + customDirectory);
        
        if (!Files.exists(scanPath)) {
            throw new IOException("Scan directory does not exist: " + customDirectory);
        }
        
        if (!Files.isDirectory(scanPath)) {
            throw new IOException("Scan path is not a directory: " + customDirectory);
        }
        
        scannedFiles.clear();
        
        try (Stream<Path> paths = Files.walk(scanPath)) {
            paths.filter(Files::isRegularFile)
                 .filter(this::isValidApplicationFile)
                 .map(Path::toFile)
                 .forEach(file -> {
                     scannedFiles.add(file);
                     logger.log("Found application file: " + file.getName());
                 });
        }
        
        logger.log("Scan completed. Found " + scannedFiles.size() + " application files");
    }

    private boolean isValidApplicationFile(Path path) {
        String fileName = path.getFileName().toString().toLowerCase();
        return VALID_EXTENSIONS.stream().anyMatch(fileName::endsWith);
    }

    public List<File> getScannedFiles() {
        return new ArrayList<>(scannedFiles);
    }

    public int getFileCount() {
        return scannedFiles.size();
    }

    public void clearScannedFiles() {
        scannedFiles.clear();
        logger.log("Cleared scanned files list");
    }
}