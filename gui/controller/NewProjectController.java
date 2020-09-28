/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.controller;

import java.io.BufferedReader;
import tl.airtoolsgui.model.SimpleLogger;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.ResourceBundle;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javafx.beans.property.IntegerProperty;
import javafx.beans.property.SimpleIntegerProperty;
import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;
import javafx.collections.FXCollections;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.Node;
import javafx.scene.control.Alert;
import javafx.scene.control.Button;
import javafx.scene.control.ChoiceBox;
import javafx.scene.control.ComboBox;
import javafx.scene.control.DatePicker;
import javafx.scene.control.Spinner;
import javafx.scene.control.SpinnerValueFactory;
import javafx.scene.control.TextField;
import javafx.scene.layout.AnchorPane;
import javafx.stage.DirectoryChooser;
import javafx.stage.Stage;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class NewProjectController implements Initializable {

    @FXML
    private AnchorPane paneNewProject;
    @FXML
    private DatePicker dpDay;
    @FXML
    private TextField tfProjectDir;
    @FXML
    private Button buttonBrowseProjectDir;
    @FXML
    private TextField tfRawDir;
    @FXML
    private Button buttonBrowseRawDir;
    @FXML
    private TextField tfTempDir;
    @FXML
    private Button buttonBrowseTempDir;
    @FXML
    private ChoiceBox<String> cbCopyParameterFiles;
    @FXML
    private ComboBox<String> cbSite;
    @FXML
    private Spinner<Integer> spinnerTZOffset;

    private SimpleLogger logger;
    private StringProperty projectDir = new SimpleStringProperty();
    private StringProperty paramDir = new SimpleStringProperty();
    private StringProperty rawDir = new SimpleStringProperty();
    private StringProperty tempDir = new SimpleStringProperty();
    private StringProperty site = new SimpleStringProperty();
    private IntegerProperty tzoff = new SimpleIntegerProperty();
    
    private final List<String> siteList = new ArrayList<>();
    private final File distDir = new File("/usr/share/airtools");
    
    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        dpDay.setValue(LocalDateTime.now().minusHours(22).toLocalDate());
        cbCopyParameterFiles.setItems(FXCollections.observableArrayList(
            "copy from last project", "create manually"));
        cbCopyParameterFiles.getSelectionModel().selectFirst();
    }    
    
    
    public void setReferences (SimpleLogger logger, StringProperty projectDir, StringProperty paramDir, StringProperty rawDir,
            StringProperty tempDir, StringProperty site, IntegerProperty  tzoff) {
        this.logger=logger;
        this.projectDir=projectDir;
        this.paramDir=paramDir;
        this.rawDir=rawDir;
        this.tempDir=tempDir;
        this.site=site;
        this.tzoff=tzoff;
        
        tfProjectDir.setText(projectDir.getValue());
        tfRawDir.setText(rawDir.getValue());
        tfTempDir.setText(tempDir.getValue());
        handleDpDayAction(null);
        
        // TODO: initialize spinnerTZOffset
        
        populateChoiceBoxSite();
        cbSite.getSelectionModel().selectFirst();
        spinnerTZOffset.setValueFactory(
            new SpinnerValueFactory.IntegerSpinnerValueFactory(-11, 12));
        spinnerTZOffset.getValueFactory().setValue(tzoff.getValue());
    }


    private void populateChoiceBoxSite () {
        System.out.println("populateChoiceBoxSite()");
        cbSite.getItems().clear();
        if (site!=null) {
            cbSite.getItems().add(site.getValue());
        }
        
        BufferedReader inFile = null;
        try {
            inFile = new BufferedReader(new FileReader(projectDir.getValue() + "/sites.dat"));
            System.out.println("Info: sites.dat found");
        } catch (FileNotFoundException ex) {
            // Logger.getLogger(CometPhotometryController.class.getName()).log(Level.SEVERE, null, ex);
            try {
                inFile = new BufferedReader(new FileReader(distDir.getPath() + "/sites.dat"));
                System.out.println("Info: " + distDir.getPath() + "/sites.dat found");
            } catch (FileNotFoundException ex2) {
                logger.log("WARNING: file " + distDir.getPath() + "/sites.dat is missing.");
                // Logger.getLogger(CometPhotometryController.class.getName()).log(Level.SEVERE, null, ex2);
            }
        }
        if (inFile == null) return;
        
        String line;
        Pattern regexp =   Pattern.compile("^[A-Z][a-zA-Z0-9]+[ ]+[a-zA-Z0-9]+[ ]+[+-]{0,1}[0-9.,]+[ ]+[+-]{0,1}[0-9.,]+[ ]+");
        Matcher matcher = regexp.matcher("");
        try {
            while (( line = inFile.readLine()) != null){
                matcher.reset(line);
                if (matcher.find()) {
                    String[] columns = line.split("[ ]+");
                    if (columns.length >= 5) {
                        // System.out.println(line);
                        System.out.println("valid site: " + columns[1]);
                        if (! columns[1].equals(site.getValue())) cbSite.getItems().add(columns[1]);
                    }
                }
            }
        } catch (IOException ex) {
            Logger.getLogger(CometPhotometryController.class.getName()).log(Level.SEVERE, null, ex);
        } finally {
            try {
                inFile.close();
            } catch (IOException ex) {
                Logger.getLogger(CometPhotometryController.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
        
    }
    
    
    private void setDayDir(TextField tf, String day) {
        String path;
        File f = new File(tf.getText());
        if (f.getName().matches("[0-9][0-9][0-9][0-9][0-9][0-9].*")) {
            path=f.getParent();
            if (path.equals("/") || path.equals("/home")) path=f.getPath();
        } else {
            path=f.getPath();
        }
        tf.setText(path + "/" + day);
    }
    
    
    @FXML
    private void handleDpDayAction(ActionEvent event) {
        String day;
        DateTimeFormatter fmt = DateTimeFormatter.ofPattern("yyMMdd");
        day = dpDay.getValue().format(fmt);
        System.out.println("day=" + day);
        
        setDayDir(tfProjectDir, day);
        setDayDir(tfRawDir, day);
        setDayDir(tfTempDir, day);
    }

    
    @FXML
    private void handleButtonBrowseProjectDirAction(ActionEvent event) {
        DirectoryChooser dirChooser = new DirectoryChooser();
        String dirName = tfProjectDir.getText();
        if (dirName.isEmpty()) {
            dirName=System.getProperty("user.home");
        }

        File file = new File(dirName);
        if (! file.isDirectory()) {
            dirName = file.getParent();
            file = new File(dirName);
            if (! file.isDirectory()) {
                dirName = file.getParent();
                file = new File(dirName);
                if (! file.isDirectory()) {
                    file = new File(System.getProperty("user.home"));
                }
            }
        }
        dirChooser.setInitialDirectory(file);
        Stage stage = (Stage) paneNewProject.getScene().getWindow();
        file = dirChooser.showDialog(stage);
        if (file != null) {
            // TODO: check for file .airtoolsrc, if missing show a warning message
            tfProjectDir.setText(file.getAbsolutePath());
        }
    }

    @FXML
    private void handleButtonBrowseRawDirAction(ActionEvent event) {
        DirectoryChooser dirChooser = new DirectoryChooser();
        String dirName = tfRawDir.getText();
        if (dirName.isEmpty()) {
            dirName=System.getProperty("user.home");
        }

        File file = new File(dirName);
        if (! file.isDirectory()) {
            dirName = file.getParent();
            file = new File(dirName);
            if (! file.isDirectory()) {
                dirName = file.getParent();
                file = new File(dirName);
                if (! file.isDirectory()) {
                    file = new File(System.getProperty("user.home"));
                }
            }
        }
        dirChooser.setInitialDirectory(file);
        Stage stage = (Stage) paneNewProject.getScene().getWindow();
        file = dirChooser.showDialog(stage);
        if (file != null) {
            // TODO: check for file .airtoolsrc, if missing show a warning message
            tfRawDir.setText(file.getAbsolutePath());
        }
    }

    @FXML
    private void handleButtonBrowseTempDirAction(ActionEvent event) {
        DirectoryChooser dirChooser = new DirectoryChooser();
        String dirName = tfTempDir.getText();
        if (dirName.isEmpty()) {
            dirName=System.getProperty("user.home");
        }

        File file = new File(dirName);
        if (! file.isDirectory()) {
            dirName = file.getParent();
            file = new File(dirName);
            if (! file.isDirectory()) {
                dirName = file.getParent();
                file = new File(dirName);
                if (! file.isDirectory()) {
                    file = new File(System.getProperty("user.home"));
                }
            }
        }
        dirChooser.setInitialDirectory(file);
        Stage stage = (Stage) paneNewProject.getScene().getWindow();
        file = dirChooser.showDialog(stage);
        if (file != null) {
            // TODO: check for file .airtoolsrc, if missing show a warning message
            tfTempDir.setText(file.getAbsolutePath());
        }
    }

    @FXML
    private void handleButtonCancelAction(ActionEvent event) {
        System.out.println("NewProjectController: Cancel");
        closeStage(event);
    }

    @FXML
    private void handleButtonApplyAction(ActionEvent event) {
        System.out.println("NewProjectController: Apply");
        //showUnderConstructionDialog();
        
        FileWriter fileWriter = null;
        DateTimeFormatter fmt = DateTimeFormatter.ofPattern("yyMMdd");
        String day = dpDay.getValue().format(fmt);
        String lastProjectDir = projectDir.getValue();
        String lastParamDir = paramDir.getValue();

        try {
            // create project directory
            File pDir = new File(tfProjectDir.getText());
            if (! pDir.exists()) {
                pDir.mkdirs();
            } else {
                // TODO: show alert if directory exists and is not empty
                logger.log("WARNING: project directory " + tfProjectDir.getText() + " already exists");
            }

            // create .airtoolsrc
            String rcFileName = tfProjectDir.getText() + "/.airtoolsrc";
            File rcFile = new File(rcFileName);
            if (! rcFile.exists()) {
                fileWriter = new FileWriter(rcFileName);
                PrintWriter printWriter = new PrintWriter(fileWriter);
                printWriter.printf("export day=%s\n", day);
                printWriter.printf("export AI_RAWDIR=%s\n", tfRawDir.getText());
                printWriter.printf("export AI_TMPDIR=%s\n", tfTempDir.getText());
                printWriter.printf("export AI_SITE=%s\n", cbSite.getSelectionModel().getSelectedItem());
                printWriter.printf("export AI_TZOFF=%s\n", spinnerTZOffset.getValue());
                printWriter.printf("export AI_EXCLUDE=\"\"\n");
                printWriter.close();
                
                // create temp directory
                File tDir = new File(tfTempDir.getText());
                if (! tDir.exists()) tDir.mkdirs();

                // update StringProperties
                rawDir.setValue(tfRawDir.getText());
                tempDir.setValue(tfTempDir.getText());
                site.setValue(cbSite.getSelectionModel().getSelectedItem());
                tzoff.setValue(spinnerTZOffset.getValue());
            }
            
            // copy parameter files
            if (cbCopyParameterFiles.getSelectionModel().getSelectedIndex() == 0) {
                File oldDir = new File(lastParamDir);
                Path oldPath = null;
                Path newPath = null;
                Path distPath = null;
                File oldFile = null;
                File newFile = null;
                File distFile = null;
                if (oldDir.exists() && oldDir.isDirectory()) {
                    // copy parameter files
                    String[] parameterFileNames = {"camera.dat", "sites.dat", "refcat.dat"};
                    for (String fileName : parameterFileNames) {
                        oldPath=Paths.get(lastParamDir + "/" + fileName);
                        newPath=Paths.get(tfProjectDir.getText() + "/" + fileName);
                        oldFile=new File(oldPath.toString());
                        newFile=new File(newPath.toString());
                        if (! newFile.exists()) {
                            if (oldFile.exists() && oldFile.isFile()) {
                                try {
                                    Files.copy(oldPath, newPath, StandardCopyOption.COPY_ATTRIBUTES);
                                } catch (IOException ex) {
                                    logger.log("ERROR: unable to copy " + fileName);
                                    Logger.getLogger(NewProjectController.class.getName()).log(Level.SEVERE, null, ex);
                                }
                            } else {
                                if (distDir.exists() && distDir.isDirectory()) {
                                    distPath=Paths.get(distDir.getPath() + "/" + fileName);
                                    distFile=new File(distPath.toString());
                                    if (distFile.exists() && distFile.isFile()) {
                                        try {
                                            Files.copy(distPath, newPath, StandardCopyOption.COPY_ATTRIBUTES);
                                        } catch (IOException ex) {
                                            logger.log("ERROR: unable to copy " + fileName + " (from DISTDIR)");
                                            Logger.getLogger(NewProjectController.class.getName()).log(Level.SEVERE, null, ex);
                                        }
                                    } else {
                                        logger.log("WARNING: missing " + distPath.toString());
                                    }
                                } else {
                                    logger.log("WARNING: missing " + oldPath.toString());
                                }
                            }
                        } else {
                            logger.log("WARNING: not overwriting file " + newPath.toString());
                        }
                    }
                }
            }

            // note: projectDir must be changed last, because it triggers saveProperties
            paramDir.setValue(tfProjectDir.getText());
            projectDir.setValue(tfProjectDir.getText());

            closeStage(event);
        } catch (IOException ex) {
            Logger.getLogger(NewProjectController.class.getName()).log(Level.SEVERE, null, ex);
        } finally {
            try {
                fileWriter.close();
            } catch (IOException ex) {
                Logger.getLogger(NewProjectController.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
    }
    
    
    private void closeStage(ActionEvent event) {
        Node  source = (Node)  event.getSource(); 
        Stage stage  = (Stage) source.getScene().getWindow();
        stage.close();
    }
    
    
    private void showUnderConstructionDialog() {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle("Information");
        alert.setHeaderText("Sorry, ...");
        alert.setContentText("this action has not been implemented yet.");
        alert.setResizable(true);
        // TODO: increase size relative to system size
        //alert.getDialogPane().setStyle("-fx-font-size: 14px;");
        //alert.getDialogPane().getScene().getWindow().sizeToScene();
        alert.getDialogPane().setMinHeight(200);
        alert.showAndWait();
    }
}
