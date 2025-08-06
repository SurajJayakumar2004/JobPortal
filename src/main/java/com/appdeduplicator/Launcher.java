package com.appdeduplicator;

import com.appdeduplicator.gui.SwingGuiMain;
import javax.swing.SwingUtilities;

public class Launcher {
    public static void main(String[] args) {
        if (args.length > 0 && args[0].equals("--cli")) {
            // Launch CLI version
            Main.main(new String[0]);
        } else if (args.length > 0 && args[0].equals("--gui")) {
            // Launch Swing GUI version
            SwingUtilities.invokeLater(() -> new SwingGuiMain());
        } else {
            // Ask user which interface to use
            System.out.println("AppDeduplicator v1.0");
            System.out.println("Choose interface:");
            System.out.println("1. GUI (Recommended)");
            System.out.println("2. CLI");
            
            java.util.Scanner scanner = new java.util.Scanner(System.in);
            System.out.print("Enter choice (1 or 2): ");
            String choice = scanner.nextLine().trim();
            scanner.close();
            
            if ("2".equals(choice)) {
                Main.main(new String[0]);
            } else {
                SwingUtilities.invokeLater(() -> new SwingGuiMain());
            }
        }
    }
}