package com.appdeduplicator;

import java.io.File;
import java.util.*;

public class DuplicateDetector {
    private final Logger logger;
    private final Map<String, List<File>> duplicateGroups;
    private final Map<File, String> fileHashes;

    public DuplicateDetector(Logger logger) {
        this.logger = logger;
        this.duplicateGroups = new HashMap<>();
        this.fileHashes = new HashMap<>();
    }

    public void findDuplicates(List<File> files) {
        duplicateGroups.clear();
        fileHashes.clear();
        
        logger.log("Starting duplicate detection for " + files.size() + " files");
        
        // Group files by hash
        Map<String, List<File>> hashGroups = new HashMap<>();
        
        for (File file : files) {
            String hash = Hasher.computeHashSafely(file, logger);
            if (hash != null) {
                fileHashes.put(file, hash);
                hashGroups.computeIfAbsent(hash, k -> new ArrayList<>()).add(file);
            }
        }
        
        // Keep only groups with more than one file (duplicates)
        for (Map.Entry<String, List<File>> entry : hashGroups.entrySet()) {
            if (entry.getValue().size() > 1) {
                duplicateGroups.put(entry.getKey(), entry.getValue());
            }
        }
        
        logger.log("Found " + duplicateGroups.size() + " duplicate groups");
        
        // Log duplicate groups
        int groupNum = 1;
        for (Map.Entry<String, List<File>> entry : duplicateGroups.entrySet()) {
            logger.log("Duplicate Group " + groupNum + " (Hash: " + entry.getKey().substring(0, 16) + "...):");
            for (File file : entry.getValue()) {
                logger.log("  - " + file.getName() + " (" + formatFileSize(file.length()) + ")");
            }
            groupNum++;
        }
    }

    public void displayDuplicates() {
        if (duplicateGroups.isEmpty()) {
            System.out.println("No duplicate files found.");
            return;
        }

        System.out.println("Found " + duplicateGroups.size() + " duplicate group(s):\n");
        
        int groupNum = 1;
        for (Map.Entry<String, List<File>> entry : duplicateGroups.entrySet()) {
            System.out.println("Group " + groupNum + " - " + entry.getValue().size() + " identical files:");
            System.out.println("Hash: " + entry.getKey().substring(0, 16) + "...");
            
            for (int i = 0; i < entry.getValue().size(); i++) {
                File file = entry.getValue().get(i);
                System.out.printf("  [%d] %s (%s)%n", 
                    i + 1, 
                    file.getName(), 
                    formatFileSize(file.length()));
                System.out.println("      Path: " + file.getAbsolutePath());
            }
            System.out.println();
            groupNum++;
        }
    }

    private String formatFileSize(long bytes) {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return String.format("%.1f KB", bytes / 1024.0);
        if (bytes < 1024 * 1024 * 1024) return String.format("%.1f MB", bytes / (1024.0 * 1024));
        return String.format("%.1f GB", bytes / (1024.0 * 1024 * 1024));
    }

    public boolean hasDuplicates() {
        return !duplicateGroups.isEmpty();
    }

    public Map<String, List<File>> getDuplicateGroups() {
        return new HashMap<>(duplicateGroups);
    }

    public String getFileHash(File file) {
        return fileHashes.get(file);
    }

    public int getTotalDuplicateFiles() {
        return duplicateGroups.values().stream()
                .mapToInt(List::size)
                .sum();
    }

    public int getDuplicateGroupCount() {
        return duplicateGroups.size();
    }
}