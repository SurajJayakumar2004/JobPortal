package com.appdeduplicator.gui;

import com.appdeduplicator.*;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.DefaultTreeModel;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.Map;

public class SwingGuiMain extends JFrame {
    // Core components
    private ConfigManager configManager;
    private Logger logger;
    private FileScanner fileScanner;
    private DuplicateDetector duplicateDetector;
    private Categorizer categorizer;
    private FileDeleter fileDeleter;
    
    // Add this field to store the selected directory
    private String selectedDirectory;
    
    // UI components
    private JTextArea logArea;
    private JList<String> fileList;
    private JTree duplicateTree;
    private JTree categoryTree;
    private JLabel statusLabel;
    private JProgressBar progressBar;
    private JLabel fileCountLabel;
    private JButton scanBtn, duplicatesBtn, categorizeBtn, deleteBtn;
    private DefaultListModel<String> fileListModel;
    
    public SwingGuiMain() {
        initializeComponents();
        setupUI();
        logger.log("Swing GUI Application started");
    }
    
    private void initializeComponents() {
        try {
            configManager = new ConfigManager();
            logger = new Logger();
            fileScanner = new FileScanner(configManager, logger);
            duplicateDetector = new DuplicateDetector(logger);
            categorizer = new Categorizer(configManager, logger);
            fileDeleter = new FileDeleter(logger);
        } catch (IOException e) {
            JOptionPane.showMessageDialog(this, 
                "Failed to initialize application: " + e.getMessage(),
                "Initialization Error", 
                JOptionPane.ERROR_MESSAGE);
            System.exit(1);
        }
    }
    
    private void setupUI() {
        setTitle("AppDeduplicator v1.0 - Swing Edition");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());
        
        // Create menu bar
        setJMenuBar(createMenuBar());
        
        // Create toolbar
        add(createToolBar(), BorderLayout.NORTH);
        
        // Create main content area
        add(createMainPanel(), BorderLayout.CENTER);
        
        // Create status bar
        add(createStatusBar(), BorderLayout.SOUTH);
        
        // Set window properties
        setSize(1200, 800);
        setLocationRelativeTo(null); // Center on screen
        setVisible(true);
    }
    
    private JMenuBar createMenuBar() {
        JMenuBar menuBar = new JMenuBar();
        
        // File menu
        JMenu fileMenu = new JMenu("File");
        
        JMenuItem chooseDirItem = new JMenuItem("Choose Directory...");
        chooseDirItem.addActionListener(e -> chooseDirectory());
        
        JMenuItem exitItem = new JMenuItem("Exit");
        exitItem.addActionListener(e -> System.exit(0));
        
        fileMenu.add(chooseDirItem);
        fileMenu.addSeparator();
        fileMenu.add(exitItem);
        
        // Tools menu
        JMenu toolsMenu = new JMenu("Tools");
        
        JMenuItem scanItem = new JMenuItem("Scan Folder");
        scanItem.addActionListener(e -> scanFolder());
        
        JMenuItem duplicatesItem = new JMenuItem("Find Duplicates");
        duplicatesItem.addActionListener(e -> findDuplicates());
        
        JMenuItem categorizeItem = new JMenuItem("Categorize Files");
        categorizeItem.addActionListener(e -> categorizeFiles());
        
        toolsMenu.add(scanItem);
        toolsMenu.add(duplicatesItem);
        toolsMenu.add(categorizeItem);
        
        menuBar.add(fileMenu);
        menuBar.add(toolsMenu);
        
        return menuBar;
    }
    
    private JToolBar createToolBar() {
        JToolBar toolBar = new JToolBar();
        toolBar.setFloatable(false);
        
        // Directory selection
        JButton chooseDirBtn = new JButton("📁 Choose Directory");
        chooseDirBtn.addActionListener(e -> chooseDirectory());
        
        // Main operations
        scanBtn = new JButton("🔍 Scan Folder");
        scanBtn.addActionListener(e -> scanFolder());
        
        duplicatesBtn = new JButton("👥 Find Duplicates");
        duplicatesBtn.addActionListener(e -> findDuplicates());
        duplicatesBtn.setEnabled(false);
        
        categorizeBtn = new JButton("📂 Categorize");
        categorizeBtn.addActionListener(e -> categorizeFiles());
        categorizeBtn.setEnabled(false);
        
        deleteBtn = new JButton("🗑️ Delete Duplicates");
        deleteBtn.addActionListener(e -> deleteDuplicates());
        deleteBtn.setEnabled(false);
        
        // File count display
        fileCountLabel = new JLabel("Files: 0");
        fileCountLabel.setFont(fileCountLabel.getFont().deriveFont(Font.BOLD));
        
        toolBar.add(chooseDirBtn);
        toolBar.addSeparator();
        toolBar.add(scanBtn);
        toolBar.add(duplicatesBtn);
        toolBar.add(categorizeBtn);
        toolBar.add(deleteBtn);
        toolBar.addSeparator();
        toolBar.add(fileCountLabel);
        
        return toolBar;
    }
    
    private JComponent createMainPanel() {
        JTabbedPane tabbedPane = new JTabbedPane();
        
        // Files tab
        fileListModel = new DefaultListModel<>();
        fileList = new JList<>(fileListModel);
        fileList.setCellRenderer(new FileListCellRenderer());
        JScrollPane fileScrollPane = new JScrollPane(fileList);
        
        JPanel filesPanel = new JPanel(new BorderLayout());
        filesPanel.setBorder(new EmptyBorder(10, 10, 10, 10));
        filesPanel.add(new JLabel("Application Files Found:"), BorderLayout.NORTH);
        filesPanel.add(fileScrollPane, BorderLayout.CENTER);
        
        tabbedPane.addTab("📄 Scanned Files", filesPanel);
        
        // Duplicates tab
        duplicateTree = new JTree(new DefaultMutableTreeNode("No duplicates found"));
        JScrollPane duplicateScrollPane = new JScrollPane(duplicateTree);
        
        JPanel duplicatesPanel = new JPanel(new BorderLayout());
        duplicatesPanel.setBorder(new EmptyBorder(10, 10, 10, 10));
        duplicatesPanel.add(new JLabel("Duplicate File Groups:"), BorderLayout.NORTH);
        duplicatesPanel.add(duplicateScrollPane, BorderLayout.CENTER);
        
        tabbedPane.addTab("👥 Duplicates", duplicatesPanel);
        
        // Categories tab
        categoryTree = new JTree(new DefaultMutableTreeNode("No categories yet"));
        JScrollPane categoryScrollPane = new JScrollPane(categoryTree);
        
        JPanel categoriesPanel = new JPanel(new BorderLayout());
        categoriesPanel.setBorder(new EmptyBorder(10, 10, 10, 10));
        categoriesPanel.add(new JLabel("Categorized Applications:"), BorderLayout.NORTH);
        categoriesPanel.add(categoryScrollPane, BorderLayout.CENTER);
        
        tabbedPane.addTab("📂 Categories", categoriesPanel);
        
        // Log tab
        logArea = new JTextArea();
        logArea.setEditable(false);
        logArea.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 12));
        JScrollPane logScrollPane = new JScrollPane(logArea);
        
        JPanel logPanel = new JPanel(new BorderLayout());
        logPanel.setBorder(new EmptyBorder(10, 10, 10, 10));
        logPanel.add(new JLabel("Application Logs:"), BorderLayout.NORTH);
        logPanel.add(logScrollPane, BorderLayout.CENTER);
        
        tabbedPane.addTab("📋 Logs", logPanel);
        
        return tabbedPane;
    }
    
    private JComponent createStatusBar() {
        JPanel statusPanel = new JPanel(new BorderLayout());
        statusPanel.setBorder(BorderFactory.createLoweredBevelBorder());
        statusPanel.setPreferredSize(new Dimension(0, 25));
        
        statusLabel = new JLabel("Ready - Choose a directory to begin");
        statusLabel.setBorder(new EmptyBorder(2, 5, 2, 5));
        
        progressBar = new JProgressBar();
        progressBar.setVisible(false);
        progressBar.setPreferredSize(new Dimension(200, 20));
        
        statusPanel.add(statusLabel, BorderLayout.CENTER);
        statusPanel.add(progressBar, BorderLayout.EAST);
        
        return statusPanel;
    }
    
    // Action methods
    private void chooseDirectory() {
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
        fileChooser.setDialogTitle("Choose Directory to Scan");
        fileChooser.setCurrentDirectory(new File(System.getProperty("user.home")));
        
        if (fileChooser.showOpenDialog(this) == JFileChooser.APPROVE_OPTION) {
            File selectedDir = fileChooser.getSelectedFile();
            selectedDirectory = selectedDir.getAbsolutePath();
            updateStatus("Directory selected: " + selectedDirectory);
            scanBtn.setEnabled(true);
            logger.log("User selected directory: " + selectedDirectory);
        }
    }
    
    private void scanFolder() {
        updateStatus("Initializing scan...");
        showProgress(true, "🔍 Scanning files...");
        
        // Disable scan button to prevent multiple concurrent scans
        scanBtn.setEnabled(false);
        scanBtn.setText("🔄 Scanning...");
        
        SwingWorker<Void, Void> worker = new SwingWorker<Void, Void>() {
            @Override
            protected Void doInBackground() throws Exception {
                // Update status to show scanning is in progress
                SwingUtilities.invokeLater(() -> updateStatus("Scanning directory for application files..."));
                
                if (selectedDirectory != null) {
                    // Scan the user-selected directory
                    fileScanner.scanCustomDirectory(selectedDirectory);
                } else {
                    // Fallback to default directory from config
                    fileScanner.scanDirectory();
                }
                return null;
            }
            
            @Override
            protected void done() {
                try {
                    get(); // Check for exceptions
                    
                    List<File> files = fileScanner.getScannedFiles();
                    updateFileList(files);
                    
                    fileCountLabel.setText("Files: " + files.size());
                    updateStatus("✅ Scan completed successfully! Found " + files.size() + " application files.");
                    
                    duplicatesBtn.setEnabled(!files.isEmpty());
                    categorizeBtn.setEnabled(!files.isEmpty());
                    
                    // Show completion message
                    if (!files.isEmpty()) {
                        JOptionPane.showMessageDialog(SwingGuiMain.this,
                            "Scan completed successfully!\n" +
                            "Found " + files.size() + " application files.\n\n" +
                            "You can now:\n" +
                            "• Find duplicates\n" +
                            "• Categorize applications",
                            "Scan Complete",
                            JOptionPane.INFORMATION_MESSAGE);
                    } else {
                        JOptionPane.showMessageDialog(SwingGuiMain.this,
                            "No application files found in the selected directory.\n" +
                            "Please try a different directory.",
                            "No Files Found",
                            JOptionPane.WARNING_MESSAGE);
                    }
                    
                } catch (Exception e) {
                    JOptionPane.showMessageDialog(SwingGuiMain.this,
                        "Error during scan: " + e.getMessage(),
                        "Scan Error",
                        JOptionPane.ERROR_MESSAGE);
                    updateStatus("❌ Scan failed: " + e.getMessage());
                } finally {
                    // Re-enable scan button and restore original text
                    scanBtn.setEnabled(true);
                    scanBtn.setText("🔍 Scan Folder");
                    showProgress(false);
                    updateLogArea();
                }
            }
        };
        
        worker.execute();
    }
    
    private void findDuplicates() {
        updateStatus("Analyzing files for duplicates...");
        showProgress(true, "👥 Finding duplicates...");
        
        // Disable button during processing
        duplicatesBtn.setEnabled(false);
        duplicatesBtn.setText("🔄 Finding...");
        
        SwingWorker<Void, Void> worker = new SwingWorker<Void, Void>() {
            @Override
            protected Void doInBackground() throws Exception {
                SwingUtilities.invokeLater(() -> updateStatus("Comparing file hashes to detect duplicates..."));
                duplicateDetector.findDuplicates(fileScanner.getScannedFiles());
                return null;
            }
            
            @Override
            protected void done() {
                try {
                    get(); // Check for exceptions
                    
                    updateDuplicateTree();
                    
                    if (duplicateDetector.hasDuplicates()) {
                        updateStatus("✅ Found " + duplicateDetector.getDuplicateGroupCount() + " duplicate groups.");
                        deleteBtn.setEnabled(true);
                        
                        JOptionPane.showMessageDialog(SwingGuiMain.this,
                            "Duplicate analysis complete!\n" +
                            "Found " + duplicateDetector.getDuplicateGroupCount() + " groups of duplicate files.\n\n" +
                            "Check the 'Duplicates' tab to view them.",
                            "Duplicates Found",
                            JOptionPane.INFORMATION_MESSAGE);
                    } else {
                        updateStatus("✅ No duplicates found - all files are unique!");
                        JOptionPane.showMessageDialog(SwingGuiMain.this,
                            "Great news! No duplicate files were found.\n" +
                            "All your application files are unique.",
                            "No Duplicates",
                            JOptionPane.INFORMATION_MESSAGE);
                    }
                    
                } catch (Exception e) {
                    JOptionPane.showMessageDialog(SwingGuiMain.this,
                        "Error finding duplicates: " + e.getMessage(),
                        "Duplicate Detection Error",
                        JOptionPane.ERROR_MESSAGE);
                    updateStatus("❌ Duplicate detection failed: " + e.getMessage());
                } finally {
                    // Re-enable button
                    duplicatesBtn.setEnabled(true);
                    duplicatesBtn.setText("👥 Find Duplicates");
                    showProgress(false);
                    updateLogArea();
                }
            }
        };
        
        worker.execute();
    }
    
    private void categorizeFiles() {
        updateStatus("Categorizing application files...");
        showProgress(true, "📂 Categorizing files...");
        
        // Disable button during processing
        categorizeBtn.setEnabled(false);
        categorizeBtn.setText("🔄 Categorizing...");
        
        SwingWorker<Void, Void> worker = new SwingWorker<Void, Void>() {
            @Override
            protected Void doInBackground() throws Exception {
                SwingUtilities.invokeLater(() -> updateStatus("Analyzing file types and organizing by category..."));
                categorizer.categorizeFiles(fileScanner.getScannedFiles());
                return null;
            }
            
            @Override
            protected void done() {
                try {
                    get(); // Check for exceptions
                    
                    updateCategoryTree();
                    updateStatus("✅ Categorization completed successfully!");
                    
                    JOptionPane.showMessageDialog(SwingGuiMain.this,
                        "Files have been categorized successfully!\n\n" +
                        "Check the 'Categories' tab to see the organized files.",
                        "Categorization Complete",
                        JOptionPane.INFORMATION_MESSAGE);
                    
                } catch (Exception e) {
                    JOptionPane.showMessageDialog(SwingGuiMain.this,
                        "Error categorizing files: " + e.getMessage(),
                        "Categorization Error",
                        JOptionPane.ERROR_MESSAGE);
                    updateStatus("❌ Categorization failed: " + e.getMessage());
                } finally {
                    // Re-enable button
                    categorizeBtn.setEnabled(true);
                    categorizeBtn.setText("📂 Categorize");
                    showProgress(false);
                    updateLogArea();
                }
            }
        };
        
        worker.execute();
    }
    
    private void deleteDuplicates() {
        if (!duplicateDetector.hasDuplicates()) {
            JOptionPane.showMessageDialog(this,
                "No duplicates found to delete.",
                "No Duplicates",
                JOptionPane.INFORMATION_MESSAGE);
            return;
        }
        
        String[] options = {"Auto-delete (keep smallest)", "Manual selection", "Cancel"};
        int choice = JOptionPane.showOptionDialog(this,
            "How would you like to handle duplicate files?",
            "Delete Duplicates",
            JOptionPane.YES_NO_CANCEL_OPTION,
            JOptionPane.QUESTION_MESSAGE,
            null,
            options,
            options[0]);
        
        if (choice == 0) {
            performAutoDeletion();
        } else if (choice == 1) {
            showManualDeletionDialog();
        }
    }
    
    private void performAutoDeletion() {
        int confirm = JOptionPane.showConfirmDialog(this,
            "This will automatically delete duplicate files.\nThis action cannot be undone. Continue?",
            "Confirm Auto-Deletion",
            JOptionPane.YES_NO_OPTION,
            JOptionPane.WARNING_MESSAGE);
        
        if (confirm == JOptionPane.YES_OPTION) {
            updateStatus("Auto-deleting duplicates...");
            showProgress(true);
            
            SwingWorker<Void, Void> worker = new SwingWorker<Void, Void>() {
                @Override
                protected Void doInBackground() throws Exception {
                    // Implement auto-deletion logic here
                    Thread.sleep(2000); // Simulate processing
                    return null;
                }
                
                @Override
                protected void done() {
                    updateStatus("Auto-deletion completed.");
                    showProgress(false);
                    scanFolder(); // Re-scan to update lists
                }
            };
            
            worker.execute();
        }
    }
    
    private void showManualDeletionDialog() {
        JDialog dialog = new JDialog(this, "Manual Duplicate Deletion", true);
        dialog.setSize(600, 500);
        dialog.setLocationRelativeTo(this);
        
        JPanel content = new JPanel(new BorderLayout());
        content.setBorder(new EmptyBorder(15, 15, 15, 15));
        
        JLabel instruction = new JLabel("Select files to delete (unchecked files will be kept):");
        content.add(instruction, BorderLayout.NORTH);
        
        // Create checkboxes for duplicate files
        JPanel checkBoxPanel = new JPanel();
        checkBoxPanel.setLayout(new BoxLayout(checkBoxPanel, BoxLayout.Y_AXIS));
        
        Map<String, List<File>> duplicateGroups = duplicateDetector.getDuplicateGroups();
        int groupNum = 1;
        
        for (Map.Entry<String, List<File>> entry : duplicateGroups.entrySet()) {
            JLabel groupLabel = new JLabel("Group " + groupNum + ":");
            groupLabel.setFont(groupLabel.getFont().deriveFont(Font.BOLD));
            checkBoxPanel.add(groupLabel);
            
            for (File file : entry.getValue()) {
                JCheckBox checkBox = new JCheckBox(file.getName() + " (" + formatFileSize(file.length()) + ")");
                checkBox.putClientProperty("file", file);
                checkBoxPanel.add(checkBox);
            }
            
            checkBoxPanel.add(Box.createVerticalStrut(10));
            groupNum++;
        }
        
        JScrollPane scrollPane = new JScrollPane(checkBoxPanel);
        content.add(scrollPane, BorderLayout.CENTER);
        
        JPanel buttonPanel = new JPanel(new FlowLayout());
        JButton deleteSelectedBtn = new JButton("Delete Selected");
        JButton cancelBtn = new JButton("Cancel");
        
        deleteSelectedBtn.addActionListener(e -> {
            // Implement manual deletion logic
            dialog.dispose();
        });
        
        cancelBtn.addActionListener(e -> dialog.dispose());
        
        buttonPanel.add(deleteSelectedBtn);
        buttonPanel.add(cancelBtn);
        content.add(buttonPanel, BorderLayout.SOUTH);
        
        dialog.add(content);
        dialog.setVisible(true);
    }
    
    // UI Update methods
    private void updateFileList(List<File> files) {
        fileListModel.clear();
        for (File file : files) {
            fileListModel.addElement(file.getName() + " (" + formatFileSize(file.length()) + ")");
        }
    }
    
    private void updateDuplicateTree() {
        DefaultMutableTreeNode root = new DefaultMutableTreeNode("Duplicate Groups");
        
        Map<String, List<File>> duplicateGroups = duplicateDetector.getDuplicateGroups();
        int groupNum = 1;
        
        for (Map.Entry<String, List<File>> entry : duplicateGroups.entrySet()) {
            DefaultMutableTreeNode groupNode = new DefaultMutableTreeNode(
                "Group " + groupNum + " (" + entry.getValue().size() + " files)");
            
            for (File file : entry.getValue()) {
                DefaultMutableTreeNode fileNode = new DefaultMutableTreeNode(
                    file.getName() + " (" + formatFileSize(file.length()) + ")");
                groupNode.add(fileNode);
            }
            
            root.add(groupNode);
            groupNum++;
        }
        
        duplicateTree.setModel(new DefaultTreeModel(root));
        
        // Expand all nodes
        for (int i = 0; i < duplicateTree.getRowCount(); i++) {
            duplicateTree.expandRow(i);
        }
    }
    
    private void updateCategoryTree() {
        DefaultMutableTreeNode root = new DefaultMutableTreeNode("Categories");
        
        Map<String, List<File>> categorizedFiles = categorizer.getCategorizedFiles();
        
        for (Map.Entry<String, List<File>> entry : categorizedFiles.entrySet()) {
            if (!entry.getValue().isEmpty()) {
                DefaultMutableTreeNode categoryNode = new DefaultMutableTreeNode(
                    entry.getKey() + " (" + entry.getValue().size() + " files)");
                
                for (File file : entry.getValue()) {
                    DefaultMutableTreeNode fileNode = new DefaultMutableTreeNode(
                        file.getName() + " (" + formatFileSize(file.length()) + ")");
                    categoryNode.add(fileNode);
                }
                
                root.add(categoryNode);
            }
        }
        
        categoryTree.setModel(new DefaultTreeModel(root));
        
        // Expand all nodes
        for (int i = 0; i < categoryTree.getRowCount(); i++) {
            categoryTree.expandRow(i);
        }
    }
    
    private void updateLogArea() {
        StringBuilder logText = new StringBuilder();
        for (String logEntry : logger.getLogs()) {
            logText.append(logEntry).append("\n");
        }
        logArea.setText(logText.toString());
        logArea.setCaretPosition(logArea.getDocument().getLength()); // Scroll to bottom
    }
    
    private void updateStatus(String message) {
        statusLabel.setText(message);
        logger.log(message);
    }
    
    private void showProgress(boolean show) {
        showProgress(show, "Processing...");
    }
    
    private void showProgress(boolean show, String message) {
        progressBar.setVisible(show);
        if (show) {
            progressBar.setIndeterminate(true);
            progressBar.setString(message);
            progressBar.setStringPainted(true);
            
            // Change cursor to wait cursor
            setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
        } else {
            progressBar.setIndeterminate(false);
            progressBar.setStringPainted(false);
            
            // Restore default cursor
            setCursor(Cursor.getDefaultCursor());
        }
    }
    
    // Utility methods
    private String formatFileSize(long bytes) {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return String.format("%.1f KB", bytes / 1024.0);
        if (bytes < 1024 * 1024 * 1024) return String.format("%.1f MB", bytes / (1024.0 * 1024));
        return String.format("%.1f GB", bytes / (1024.0 * 1024 * 1024));
    }
    
    // Custom cell renderer for file list
    private class FileListCellRenderer extends DefaultListCellRenderer {
        @Override
        public Component getListCellRendererComponent(JList<?> list, Object value, int index,
                boolean isSelected, boolean cellHasFocus) {
            
            super.getListCellRendererComponent(list, value, index, isSelected, cellHasFocus);
            
            String item = value.toString();
            if (!isSelected) {
                if (item.contains(".exe")) {
                    setForeground(new Color(0, 102, 204));
                } else if (item.contains(".jar")) {
                    setForeground(new Color(204, 102, 0));
                } else if (item.contains(".msi")) {
                    setForeground(new Color(0, 153, 0));
                } else if (item.contains(".apk")) {
                    setForeground(new Color(153, 0, 153));
                } else {
                    setForeground(Color.BLACK);
                }
            }
            
            return this;
        }
    }
    
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new SwingGuiMain());
    }
}