package main

import (
	"fmt"
	// "io"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/otiai10/gosseract/v2"
	"github.com/pdfcpu/pdfcpu/pkg/api"
	"github.com/pdfcpu/pdfcpu/pkg/pdfcpu"
)

const uploadFolder = "uploads"
const allowedExtensions = "pdf"

func main() {
	router := gin.Default()

	router.POST("/upload", uploadFile)

	if err := router.Run(":5002"); err != nil {
		fmt.Println("Error starting server:", err)
	}
}

func uploadFile(c *gin.Context) {
	file, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No file part"})
		return
	}

	if !isAllowedFile(file.Filename) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file format"})
		return
	}

	if err := createUploadFolder(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create upload folder"})
		return
	}

	// Save the uploaded file
	filename := filepath.Join(uploadFolder, file.Filename)
	if err := c.SaveUploadedFile(file, filename); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
		return
	}

	// Perform OCRmyPDF conversion
	outputFilename := strings.TrimSuffix(file.Filename, filepath.Ext(file.Filename)) + "_ArcorOCR.pdf"
	outputFilepath := filepath.Join(uploadFolder, outputFilename)

	if err := performOCR(filename, outputFilepath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "OCR conversion failed"})
		return
	}

	// Send the converted file as an attachment
	c.Header("Content-Disposition", "attachment; filename="+outputFilename)
	c.Header("Content-Type", "application/pdf")
	c.File(outputFilepath)

	// Cleanup: Delete the original and converted files after sending
	if err := cleanupFiles(filename, outputFilepath); err != nil {
		fmt.Println("Error cleaning up files:", err)
	}
}

func createUploadFolder() error {
	if _, err := os.Stat(uploadFolder); os.IsNotExist(err) {
		return os.Mkdir(uploadFolder, 0755)
	}
	return nil
}

func isAllowedFile(filename string) bool {
	ext := strings.ToLower(filepath.Ext(filename))
	return ext == "."+allowedExtensions
}

func performOCR(inputFile, outputFile string) error {
	// Convert PDF to images using custom function
	imgFolder := filepath.Join(uploadFolder, "images")
	if err := convertPDFToImages(inputFile, imgFolder); err != nil {
		return err
	}
	defer os.RemoveAll(imgFolder)

	// Perform OCR on each image
	client := gosseract.NewClient()
	defer client.Close()

	client.SetLanguage("eng") // Set the language as needed

	// Create a new PDF file to store the OCR results
	pdfWriter := pdfcpu.NewWriter(outputFile)

	// Iterate over the images and perform OCR
	err := filepath.Walk(imgFolder, func(imgPath string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if !info.IsDir() {
			client.SetImage(imgPath)
			text, err := client.Text()
			if err != nil {
				return err
			}

			// Add the extracted text to the new PDF file
			page := pdfcpu.Page{
				Images: []pdfcpu.Image{
					{FileName: imgPath},
				},
				Text: []string{text},
			}
			if err := pdfWriter.AddPage(page); err != nil {
				return err
			}
		}

		return nil
	})

	if err != nil {
		return err
	}

	// Write the final PDF file with OCR results
	if err := pdfWriter.Write(); err != nil {
		return err
	}

	return nil
}

func convertPDFToImages(inputFile, outputFolder string) error {
	return api.ExtractImagesFile(inputFile, outputFolder, nil, nil)
}

func cleanupFiles(files ...string) error {
	for _, file := range files {
		if err := os.Remove(file); err != nil {
			return err
		}
	}
	return nil
}
