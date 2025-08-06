package com.appdeduplicator;

import java.io.File;
import java.util.*;

public class Categorizer {
    private final ConfigManager configManager;
    private final Logger logger;
    private final Map<String, List<File>> categorizedFiles;

    public Categorizer(ConfigManager configManager, Logger logger) {
        this.configManager = configManager;
        this.logger = logger;
        this.categorizedFiles = new HashMap<>();
    }

    public void categorizeFiles(List<File> files) {
        categorizedFiles.clear();
        
        logger.log("Starting categorization of " + files.size() + " files");
        
        // Initialize categories
        for (String category : configManager.getCategories()) {
            categorizedFiles.put(category, new ArrayList<>());
        }
        categorizedFiles.put("Uncategorized", new ArrayList<>());
        
        // Categorize each file
        for (File file : files) {
            String category = categorizeFile(file);
            categorizedFiles.get(category).add(file);
            logger.log("Categorized " + file.getName() + " as " + category);
        }
        
        logger.log("Categorization completed");
    }

    private String categorizeFile(File file) {
        String fileName = file.getName().toLowerCase();
        
        // Check each category
        for (String category : configManager.getCategories()) {
            List<String> keywords = configManager.getKeywordsForCategory(category);
            
            for (String keyword : keywords) {
                if (fileName.contains(keyword.toLowerCase())) {
                    return category;
                }
            }
        }
        
        return "Uncategorized";
    }

    public void displayCategorizedFiles() {
        if (categorizedFiles.isEmpty()) {
            System.out.println("No files have been categorized yet.");
            return;
        }

        System.out.println("=== Categorized Applications ===\n");
        
        for (Map.Entry<String, List<File>> entry : categorizedFiles.entrySet()) {
            String category = entry.getKey();
            List<File> files = entry.getValue();
            
            if (!files.isEmpty()) {
                System.out.println("📁 " + category + " (" + files.size() + " files):");
                
                for (File file : files) {
                    System.out.printf("  • %s (%s)%n", 
                        file.getName(), 
                        formatFileSize(file.length()));
                    System.out.println("    Path: " + file.getAbsolutePath());
                }
                System.out.println();
            }
        }
        
        // Summary
        int totalFiles = categorizedFiles.values().stream()
                .mapToInt(List::size)
                .sum();
        
        System.out.println("--- Summary ---");
        System.out.println("Total files: " + totalFiles);
        System.out.println("Categories with files: " + 
            categorizedFiles.entrySet().stream()
                .mapToInt(entry -> entry.getValue().isEmpty() ? 0 : 1)
                .sum());
    }

    public Map<String, List<File>> getCategorizedFiles() {
        return new HashMap<>(categorizedFiles);
    }

    public List<File> getFilesInCategory(String category) {
        return new ArrayList<>(categorizedFiles.getOrDefault(category, new ArrayList<>()));
    }

    public int getTotalCategorizedFiles() {
        return categorizedFiles.values().stream()
                .mapToInt(List::size)
                .sum();
    }

    private String formatFileSize(long bytes) {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return String.format("%.1f KB", bytes / 1024.0);
        if (bytes < 1024 * 1024 * 1024) return String.format("%.1f MB", bytes / (1024.0 * 1024));
        return String.format("%.1f GB", bytes / (1024.0 * 1024 * 1024));
    }
}