package com.appdeduplicator;

import java.io.File;
import java.util.*;

public class FileDeleter {
    private final Logger logger;

    public FileDeleter(Logger logger) {
        this.logger = logger;
    }

    public void handleDuplicateDeletion(Map<String, List<File>> duplicateGroups, Scanner scanner) {
        if (duplicateGroups.isEmpty()) {
            System.out.println("No duplicate groups to process.");
            return;
        }

        System.out.println("Found " + duplicateGroups.size() + " duplicate group(s)");
        System.out.println("Choose deletion mode:");
        System.out.println("1. Interactive deletion (choose files manually)");
        System.out.println("2. Auto-delete (keep smallest file from each group)");
        System.out.println("3. Cancel");
        System.out.print("Select option (1-3): ");
        
        String choice = scanner.nextLine().trim();
        
        switch (choice) {
            case "1":
                interactiveDeletion(duplicateGroups, scanner);
                break;
            case "2":
                autoDeletion(duplicateGroups);
                break;
            case "3":
                System.out.println("Deletion cancelled.");
                return;
            default:
                System.out.println("Invalid choice. Deletion cancelled.");
                return;
        }
    }

    private void interactiveDeletion(Map<String, List<File>> duplicateGroups, Scanner scanner) {
        int groupNum = 1;
        int totalDeleted = 0;
        
        for (Map.Entry<String, List<File>> entry : duplicateGroups.entrySet()) {
            System.out.println("\n--- Group " + groupNum + " ---");
            List<File> files = entry.getValue();
            
            for (int i = 0; i < files.size(); i++) {
                File file = files.get(i);
                System.out.printf("[%d] %s (%s)%n", 
                    i + 1, 
                    file.getName(), 
                    formatFileSize(file.length()));
                System.out.println("    Path: " + file.getAbsolutePath());
            }
            
            System.out.print("Enter numbers to delete (e.g., 1,3) or 'skip' to skip group: ");
            String input = scanner.nextLine().trim();
            
            if (input.equalsIgnoreCase("skip")) {
                System.out.println("Skipped group " + groupNum);
                groupNum++;
                continue;
            }
            
            try {
                String[] indices = input.split(",");
                List<Integer> toDelete = new ArrayList<>();
                
                for (String index : indices) {
                    int idx = Integer.parseInt(index.trim()) - 1;
                    if (idx >= 0 && idx < files.size()) {
                        toDelete.add(idx);
                    }
                }
                
                // Sort in reverse order to avoid index shifting
                toDelete.sort(Collections.reverseOrder());
                
                for (int idx : toDelete) {
                    File fileToDelete = files.get(idx);
                    if (deleteFile(fileToDelete)) {
                        totalDeleted++;
                    }
                }
                
            } catch (NumberFormatException e) {
                System.out.println("Invalid input format. Skipping group.");
            }
            
            groupNum++;
        }
        
        System.out.println("\nDeletion completed. Total files deleted: " + totalDeleted);
        logger.log("Interactive deletion completed. Files deleted: " + totalDeleted);
    }

    private void autoDeletion(Map<String, List<File>> duplicateGroups) {
        int totalDeleted = 0;
        
        System.out.println("Auto-deletion mode: keeping smallest file from each group...");
        
        for (Map.Entry<String, List<File>> entry : duplicateGroups.entrySet()) {
            List<File> files = entry.getValue();
            
            // Find the smallest file
            File smallest = files.stream()
                    .min(Comparator.comparing(File::length))
                    .orElse(files.get(0));
            
            System.out.println("Group: Keeping " + smallest.getName() + 
                    " (" + formatFileSize(smallest.length()) + ")");
            
            // Delete all other files
            for (File file : files) {
                if (!file.equals(smallest)) {
                    if (deleteFile(file)) {
                        totalDeleted++;
                    }
                }
            }
        }
        
        System.out.println("\nAuto-deletion completed. Total files deleted: " + totalDeleted);
        logger.log("Auto-deletion completed. Files deleted: " + totalDeleted);
    }

    private boolean deleteFile(File file) {
        try {
            if (file.delete()) {
                System.out.println("✓ Deleted: " + file.getName());
                logger.log("Deleted file: " + file.getAbsolutePath());
                return true;
            } else {
                System.out.println("✗ Failed to delete: " + file.getName());
                logger.log("Failed to delete file: " + file.getAbsolutePath());
                return false;
            }
        } catch (SecurityException e) {
            System.out.println("✗ Permission denied: " + file.getName());
            logger.log("Permission denied deleting file: " + file.getAbsolutePath() + " - " + e.getMessage());
            return false;
        }
    }

    private String formatFileSize(long bytes) {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return String.format("%.1f KB", bytes / 1024.0);
        if (bytes < 1024 * 1024 * 1024) return String.format("%.1f MB", bytes / (1024.0 * 1024));
        return String.format("%.1f GB", bytes / (1024.0 * 1024 * 1024));
    }
}