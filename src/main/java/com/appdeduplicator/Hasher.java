package com.appdeduplicator;

import org.apache.commons.codec.digest.DigestUtils;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class Hasher {
    
    /**
     * Computes SHA-256 hash of a file using Apache Commons Codec
     */
    public static String computeSHA256(File file) throws IOException {
        try (FileInputStream fis = new FileInputStream(file)) {
            return DigestUtils.sha256Hex(fis);
        }
    }
    
    /**
     * Alternative implementation using Java's MessageDigest
     */
    public static String computeSHA256Alternative(File file) throws IOException, NoSuchAlgorithmException {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        
        try (FileInputStream fis = new FileInputStream(file)) {
            byte[] buffer = new byte[8192];
            int bytesRead;
            
            while ((bytesRead = fis.read(buffer)) != -1) {
                digest.update(buffer, 0, bytesRead);
            }
        }
        
        byte[] hashBytes = digest.digest();
        StringBuilder hexString = new StringBuilder();
        
        for (byte b : hashBytes) {
            String hex = Integer.toHexString(0xff & b);
            if (hex.length() == 1) {
                hexString.append('0');
            }
            hexString.append(hex);
        }
        
        return hexString.toString();
    }
    
    /**
     * Computes hash with error handling and logging
     */
    public static String computeHashSafely(File file, Logger logger) {
        try {
            String hash = computeSHA256(file);
            logger.log("Computed hash for " + file.getName() + ": " + hash.substring(0, 16) + "...");
            return hash;
        } catch (IOException e) {
            logger.log("Error computing hash for " + file.getName() + ": " + e.getMessage());
            return null;
        }
    }
}