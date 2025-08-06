package com.appdeduplicator;

import java.util.Scanner;

public class Main {
    private static final Scanner scanner = new Scanner(System.in);
    private static FileScanner fileScanner;
    private static DuplicateDetector duplicateDetector;
    private static Categorizer categorizer;
    private static FileDeleter fileDeleter;
    private static Logger logger;
    private static ConfigManager configManager;

    public static void main(String[] args) {
        System.out.println("=== AppDeduplicator v1.0 ===");
        System.out.println("Application File Management Tool\n");

        try {
            // Initialize components
            configManager = new ConfigManager();
            logger = new Logger();
            fileScanner = new FileScanner(configManager, logger);
            duplicateDetector = new DuplicateDetector(logger);
            categorizer = new Categorizer(configManager, logger);
            fileDeleter = new FileDeleter(logger);

            logger.log("Application started");
            
            // Main menu loop
            boolean running = true;
            while (running) {
                showMenu();
                int choice = getMenuChoice();
                
                switch (choice) {
                    case 1:
                        scanFolder();
                        break;
                    case 2:
                        showDuplicates();
                        break;
                    case 3:
                        deleteDuplicates();
                        break;
                    case 4:
                        categorizeApplications();
                        break;
                    case 5:
                        showCategorizedList();
                        break;
                    case 6:
                        viewLogReport();
                        break;
                    case 7:
                        running = false;
                        System.out.println("Exiting AppDeduplicator. Goodbye!");
                        logger.log("Application terminated");
                        break;
                    default:
                        System.out.println("Invalid option. Please try again.");
                }
                
                if (running) {
                    System.out.println("\nPress Enter to continue...");
                    scanner.nextLine();
                }
            }
        } catch (Exception e) {
            System.err.println("Fatal error: " + e.getMessage());
            e.printStackTrace();
        } finally {
            scanner.close();
        }
    }

    private static void showMenu() {
        System.out.println("\n" + "=".repeat(40));
        System.out.println("           MAIN MENU");
        System.out.println("=".repeat(40));
        System.out.println("1. Scan Folder");
        System.out.println("2. Show Duplicates");
        System.out.println("3. Delete Duplicates");
        System.out.println("4. Categorize Applications");
        System.out.println("5. Show Categorized List");
        System.out.println("6. View Log Report");
        System.out.println("7. Exit");
        System.out.println("=".repeat(40));
        System.out.print("Select an option (1-7): ");
    }

    private static int getMenuChoice() {
        try {
            String input = scanner.nextLine().trim();
            return Integer.parseInt(input);
        } catch (NumberFormatException e) {
            return -1;
        }
    }

    private static void scanFolder() {
        System.out.println("\n--- Scanning Folder ---");
        try {
            fileScanner.scanDirectory();
            System.out.println("Scan completed successfully!");
            System.out.println("Found " + fileScanner.getScannedFiles().size() + " application files.");
        } catch (Exception e) {
            System.err.println("Error during scan: " + e.getMessage());
        }
    }

    private static void showDuplicates() {
        System.out.println("\n--- Duplicate Files ---");
        try {
            if (fileScanner.getScannedFiles().isEmpty()) {
                System.out.println("No files scanned yet. Please scan folder first.");
                return;
            }
            
            duplicateDetector.findDuplicates(fileScanner.getScannedFiles());
            duplicateDetector.displayDuplicates();
        } catch (Exception e) {
            System.err.println("Error finding duplicates: " + e.getMessage());
        }
    }

    private static void deleteDuplicates() {
        System.out.println("\n--- Delete Duplicates ---");
        try {
            if (!duplicateDetector.hasDuplicates()) {
                System.out.println("No duplicates found. Please scan and find duplicates first.");
                return;
            }
            
            fileDeleter.handleDuplicateDeletion(duplicateDetector.getDuplicateGroups(), scanner);
        } catch (Exception e) {
            System.err.println("Error deleting duplicates: " + e.getMessage());
        }
    }

    private static void categorizeApplications() {
        System.out.println("\n--- Categorizing Applications ---");
        try {
            if (fileScanner.getScannedFiles().isEmpty()) {
                System.out.println("No files scanned yet. Please scan folder first.");
                return;
            }
            
            categorizer.categorizeFiles(fileScanner.getScannedFiles());
            System.out.println("Categorization completed!");
        } catch (Exception e) {
            System.err.println("Error categorizing files: " + e.getMessage());
        }
    }

    private static void showCategorizedList() {
        System.out.println("\n--- Categorized Applications ---");
        try {
            categorizer.displayCategorizedFiles();
        } catch (Exception e) {
            System.err.println("Error displaying categorized files: " + e.getMessage());
        }
    }

    private static void viewLogReport() {
        System.out.println("\n--- Log Report ---");
        try {
            logger.displayReport();
        } catch (Exception e) {
            System.err.println("Error viewing log report: " + e.getMessage());
        }
    }
}