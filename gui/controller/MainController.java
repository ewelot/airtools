package tl.airtoolsgui.controller;

/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */


import java.io.BufferedReader;
import tl.airtoolsgui.model.ShellScript;
import tl.airtoolsgui.model.SimpleLogger;

import java.io.File;
import java.net.URL;
import java.util.ResourceBundle;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.CheckBox;
import javafx.scene.control.Label;
import javafx.scene.layout.BorderPane;
import javafx.stage.Stage;

import javafx.application.Platform;
import javafx.beans.binding.Bindings;
import javafx.scene.control.TextArea;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Optional;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javafx.beans.property.IntegerProperty;
import javafx.beans.property.SimpleIntegerProperty;
import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;
import javafx.event.Event;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Alert;
import javafx.scene.control.Alert.AlertType;
import javafx.scene.control.ButtonBar.ButtonData;
import javafx.scene.control.ButtonType;
import javafx.scene.control.Menu;
import javafx.scene.control.MenuItem;
import javafx.scene.control.Tab;
import javafx.scene.control.TabPane;
import javafx.scene.layout.Region;
import javafx.scene.layout.VBox;
import javafx.stage.DirectoryChooser;
import javafx.stage.FileChooser;
import javafx.stage.Modality;
import tl.airtoolsgui.model.Observer;
import tl.airtoolsgui.model.SitesList;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class MainController implements Initializable {

    @FXML
    private BorderPane appPane;
    @FXML
    private CheckBox cbAutoScroll;
    @FXML
    private TextArea textareaLog;
    @FXML
    private Label labelInfo;
    @FXML
    private Label labelStatus;


    @FXML
    private Menu menuFile;
    @FXML
    private MenuItem menuNewProject;
    @FXML
    private MenuItem menuOpenProject;
    @FXML
    private MenuItem menuArchive;
    @FXML
    private MenuItem menuExit;

    @FXML
    private Menu menuEdit;
    @FXML
    private MenuItem menuProjectSettings;
    @FXML
    private MenuItem menuEditImageSet;
    @FXML
    private MenuItem menuEditSiteParam;
    @FXML
    private MenuItem menuEditCameraParam;

    @FXML
    private Menu menuAnalysis;
    @FXML
    private MenuItem menuBadPixel;
    @FXML
    private MenuItem menuList;
    @FXML
    private MenuItem menuLightCurve;
    @FXML
    private MenuItem menuMapPhot;
    @FXML
    private MenuItem menuAstrometry;

    @FXML
    private Menu menuHelp;
    @FXML
    private MenuItem menuManual;
    @FXML
    private MenuItem menuEnvironment;
    @FXML
    private MenuItem menuDependencies;
    @FXML
    private MenuItem menuAbout;

    @FXML
    private TabPane tabPane;
    @FXML
    private Tab tabImageReduction;
    @FXML
    private Tab tabCometPhotometry;
    @FXML
    private Tab tabMiscTools;

    // Inject controllers (add required @FXML annotation)
    @FXML
    private ImageReductionController paneImageReductionController;
    @FXML
    private CometPhotometryController paneCometPhotometryController;
    @FXML
    private MiscToolsController paneMiscToolsController;

    // additional windows (stages)
    private Stage windowArchive;
    private Stage windowCreateBadpixelMask;
    private Stage windowListResults;
    private Stage windowLightCurve;
    private Stage windowMultiApPhotometry;
    private Stage windowAstrometry;
    
    private Properties projectProperties;
    private String configFile;
    private SimpleLogger logger;
    private ShellScript sh;
    private String progVersion;
    private String progDate;
    private final String onlineManualURL = "https://github.com/ewelot/airtools/blob/master/doc/manual-en.md";
    private final StringProperty projectDir = new SimpleStringProperty();
    private final StringProperty rawDir = new SimpleStringProperty();
    private final StringProperty tempDir = new SimpleStringProperty();
    private final StringProperty site = new SimpleStringProperty();
    private final IntegerProperty tzoff = new SimpleIntegerProperty();
    private Observer observer;
    
    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        System.out.println("MainController: initialize");
        //projectDir.setValue("");
        projectDir.addListener( (v, oldValue, newValue) -> {
            onProjectDirChange();
        });
        
        // "File" menu actions
        menuNewProject.setOnAction((event) -> {
            showNewProjectDialog();
        });
        menuOpenProject.setOnAction((event) -> {
            openExistingProject();
        });
        menuArchive.setOnAction((event) -> {
            showWindowArchive();
        });
        menuExit.setOnAction((event) -> {
            Platform.exit();
        });
        
        // "Edit" menu actions
        menuProjectSettings.setOnAction((event) -> {
            startTextEditor(".airtoolsrc", false);
        });
        menuEditImageSet.setOnAction((event) -> {
            startTextEditor("set.dat", false);
        });
        menuEditSiteParam.setOnAction((event) -> {
            startTextEditor("sites.dat", true);
        });
        menuEditCameraParam.setOnAction((event) -> {
            startTextEditor("camera.dat", true);
        });
        
        // "Analysis" menu actions
        menuBadPixel.setOnAction((event) -> {
            //listResults();
            showWindowCreateBadpixelMask();
        });
        menuList.setOnAction((event) -> {
            //listResults();
            showWindowListResults();
        });
        menuLightCurve.setOnAction((event) -> {
            showWindowLightCurve();
        });
        menuMapPhot.setOnAction((event) -> {
            showWindowMultiApPhotometry();
        });
        menuAstrometry.setOnAction((event) -> {
            showWindowAstrometry();
        });
        
        // "Help" menu actions
        menuManual.setOnAction((event) -> {
            openOnlineManual();
        });
        menuEnvironment.setOnAction((event) -> {
            paneMiscToolsController.showEnvironment();
        });
        menuDependencies.setOnAction((event) -> {
            checkDependencies();
        });
        menuAbout.setOnAction((event) -> {
            showAboutDialog();
        });

        // Layout
        textareaLog.setStyle("-fx-font-family: monospace");
        labelInfo.setStyle("-fx-background-color: white;"
                + "-fx-text-fill: gray;");
        labelStatus.setStyle("-fx-background-color: white;"
                + "-fx-text-fill: gray;");
        
        /*
        labelInfo.textProperty().bind(
            Bindings.concat(
                textareaLog.scrollTopProperty().asString("%.0f / "),
                textareaLog.heightProperty().asString("%.0f")));
        */

        labelInfo.textProperty().bind(
            Bindings.createStringBinding(() -> {
                String pDir = projectDir.getValue();
                if (pDir != null) {
                    int start=pDir.lastIndexOf("/") + 1;
                    return pDir.substring(start);
                } else {
                    return "";
                }
            }, projectDir));

    }

    public SimpleLogger getLogger() {
        return logger;
    }
    
    public StringProperty getProjectDir () {
        return projectDir;
    }

    
    public void setReferences (String confFileName, ShellScript sh, SimpleLogger logger, String progVersion, String progDate) {
        System.out.println("MainController: setReferences");
        this.configFile = confFileName;
        this.sh = sh;
        this.logger = logger;
        this.progVersion = progVersion;
        this.progDate = progDate;
        
        logger.setLogArea(textareaLog);
        logger.setAutoScroll(cbAutoScroll);
        logger.setStatusLine(labelStatus);
        logger.statusLog("Ready");
        
        /* read initial project settings from config file */
        projectProperties = new Properties();
        loadProperties(configFile);
        rawDir.setValue(projectProperties.getProperty("lastRawDir", "/tmp"));
        tempDir.setValue(projectProperties.getProperty("lastTempDir", "/tmp"));
        site.setValue(projectProperties.getProperty("lastSite", ""));
        observer = new Observer(projectProperties.getProperty("lastObsName", ""),
            projectProperties.getProperty("lastObsAddress", ""),
            projectProperties.getProperty("lastObsEmail", ""),
            projectProperties.getProperty("lastObsIcqID", ""));
        if (observer.getIcqID().isBlank()) {
            observer.setIcqID(projectProperties.getProperty("lastObserver", ""));
        }
        int i=0;
        String str = projectProperties.getProperty("lastTZOff", "0");
        if (str != null && ! str.isEmpty()) {
            try {
                i=Integer.parseInt(str);
            } catch (NumberFormatException e) {
                logger.log("WARNING: unable to convert lastTZoff in " + confFileName);
            }
        }
        tzoff.setValue(i);

        paneImageReductionController.setReferences(sh, logger);
        paneCometPhotometryController.setReferences(sh, logger);        
        paneCometPhotometryController.projectDir.bind(projectDir);
        paneMiscToolsController.setReferences(sh, logger);        
        paneMiscToolsController.projectDir.bind(projectDir);
        

        String val;
        val = projectProperties.getProperty("lastProjectDir");
        
        if (val == null || val.isEmpty()) {
            val=System.getProperty("user.home");
        } else {
            File inFile = new File(val);
            if (! inFile.exists() || ! inFile.isDirectory()) val=System.getProperty("user.home");
        }
        projectDir.setValue(val);
        sh.setWorkingDir(val);
    }
    
    
    private void onProjectDirChange() {
        System.out.println("onProjectDirChange()");
        logger.log("Project Directory = " + projectDir.getValue());
        sh.setWorkingDir(projectDir.getValue());
        paneImageReductionController.clearTabContent();
        paneCometPhotometryController.clearTabContent();
        paneMiscToolsController.clearTabContent();

        paneCometPhotometryController.updateTabContent();
        if (! paneCometPhotometryController.hasImageSets())
            tabPane.getSelectionModel().selectFirst();

        projectProperties.setProperty("lastProjectDir", projectDir.getValue());
        //projectProperties.setProperty("lastRawDir", rawDir.getValue());
        //projectProperties.setProperty("lastTempDir", tempDir.getValue());
        projectProperties.setProperty("lastSite", site.getValue());
        projectProperties.setProperty("lastTZOff", tzoff.getValue().toString());
        projectProperties.setProperty("lastObsName", observer.getName());
        projectProperties.setProperty("lastObsAddress", observer.getAddress());
        projectProperties.setProperty("lastObsEmail", observer.getEmail());
        projectProperties.setProperty("lastObsIcqID", observer.getIcqID());

        // remove unused/old properties
        if (projectProperties.containsKey("lastParamDir"))
            projectProperties.remove("lastParamDir");
        if (projectProperties.containsKey("lastObsID"))
            projectProperties.remove("lastObsID");

        saveProperties(configFile);
    }

    
    private void loadProperties(String fileName) {
        try {
            InputStream inputStream = new FileInputStream(fileName);
            projectProperties.load(inputStream);
            inputStream.close();
        } catch (FileNotFoundException ex) {
            logger.log("WARNING: conf file " + configFile + " not found");
        } catch (IOException ex) {
            logger.log("WARNING: unable to read conf file (IO Error)");
        }
        
    }
    
    
    private void saveProperties(String fileName) {
        try {
            // store global settings
            OutputStream outputStream = new FileOutputStream(fileName);
            projectProperties.store(outputStream, "global settings");
            outputStream.close();
        } catch (IOException ex) {
            Logger.getLogger(MainController.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
    
    public String byteToHex(byte num) {
        char[] hexDigits = new char[2];
        hexDigits[0] = Character.forDigit((num >> 4) & 0xF, 16);
        hexDigits[1] = Character.forDigit((num & 0xF), 16);
        return new String(hexDigits);
    }
    
    public String encodeHexString(byte[] byteArray) {
        // convert byteArray to String
        StringBuffer hexStringBuffer = new StringBuffer();
        for (int i = 0; i < byteArray.length; i++) {
            hexStringBuffer.append(byteToHex(byteArray[i]));
        }
        return hexStringBuffer.toString();
    }
    
    private void startTextEditor(String fileName, boolean isParamFile) {
        System.out.println("startTextEditor()");
        File textFile = null;
        String dir = projectDir.getValue();
        if (fileName != null && ! fileName.isEmpty()) {
            if (dir != null && ! dir.isEmpty()) {
                textFile = new File(dir + "/" + fileName);
            }
        } else {
            FileChooser fileChooser = new FileChooser();
            if (dir != null && ! dir.isEmpty()) {
                File file = new File(dir);
                if (file != null) fileChooser.setInitialDirectory(file);
            }
            textFile = fileChooser.showOpenDialog(this.appPane.getScene().getWindow());
        }
        if (textFile == null) return;
        
        if (! textFile.exists()) createFileFromTemplate(textFile, isParamFile);

        
        if (textFile.exists()) {
            ProcessBuilder pb = new ProcessBuilder("/bin/bash", "-c", "mousepad " + textFile.getAbsolutePath());
            try {
                MessageDigest md = MessageDigest.getInstance("MD5");
                md.update(Files.readAllBytes(Paths.get(textFile.getAbsolutePath())));
                String origChecksum = encodeHexString(md.digest());
                Process editorProcess = pb.start();
                if (isParamFile) {
                    editorProcess.waitFor();
                    // TODO: if file has changed then ask user if it should be copied to config dir
                    md.update(Files.readAllBytes(Paths.get(textFile.getAbsolutePath())));
                    String newChecksum = encodeHexString(md.digest());
                    if (! newChecksum.equals(origChecksum)) {
                        Alert alert = new Alert(AlertType.CONFIRMATION);
                        alert.setTitle("Confirmation Dialog");
                        alert.setHeaderText("The parameter file " + fileName + " has been modified.");
                        alert.setContentText("Would you like to use it as default for new projects?\n\n");

                        Optional<ButtonType> result = alert.showAndWait();
                        if (result.get() == ButtonType.OK){
                            Files.copy(Paths.get(textFile.getAbsolutePath()), Path.of(configFile).getParent().resolve(fileName),
                                    StandardCopyOption.COPY_ATTRIBUTES, StandardCopyOption.REPLACE_EXISTING);
                            logger.log("# local file " + fileName + " copied to " + Path.of(configFile).getParent());
                        } else {
                            logger.log("# WARNING: file " + fileName + " not copied to " + Path.of(configFile).getParent());
                        }
                    }
                }
            } catch (IOException ex) {
                Logger.getLogger(MainController.class.getName()).log(Level.SEVERE, null, ex);
            } catch (InterruptedException ex) {
                Logger.getLogger(MainController.class.getName()).log(Level.SEVERE, null, ex);
            } catch (NoSuchAlgorithmException ex) {
                // MD5 not found
                Logger.getLogger(MainController.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
    }
    

    private void createFileFromTemplate(File destFile, boolean isParamFile) {
        File srcFile = null;
        File lastUsedFile = null;
        Path confPath;
        File testFile;
        
        /* check for last used file by examining configdir */
        if (isParamFile) {
            confPath = Path.of(configFile).getParent();
            testFile = new File(confPath + "/" + destFile.getName());
            if (testFile.exists()) {
                lastUsedFile = testFile;
                logger.log("# INFO: parameter file " + testFile.getAbsolutePath() + " exists.");
            } else {
                logger.log("# WARNING: parameter file " + testFile.getAbsolutePath() + " does not exist.");
            }
            
            /* check for last used file by examining previous configdir */
            if (lastUsedFile == null) {
                // if last version is 3: check lastParamDir in ~/.airtools/3/airtools.conf
                String confFileName = Path.of(configFile).getParent().getParent() + "/3/airtools.conf";
                Properties oldProperties = new Properties();
                try {
                    InputStream inputStream = new FileInputStream(confFileName);
                    oldProperties.load(inputStream);
                    inputStream.close();
                    testFile = new File(oldProperties.getProperty("lastParamDir") + "/" + destFile.getName());
                    if (testFile.exists()) {
                        lastUsedFile = testFile;
                        logger.log("# INFO: parameter file " + testFile.getAbsolutePath() + " exists.");
                    } else {
                        logger.log("# WARNING: parameter file " + testFile.getAbsolutePath() + " does not exist.");
                    }
                } catch (FileNotFoundException ex) {
                    logger.log("WARNING: old config file " + confFileName + " not found");
                } catch (IOException ex) {
                    logger.log("WARNING: unable to read old config file (IO Error)");
                }
            }
        }
        
        Alert alert = new Alert(AlertType.CONFIRMATION);
        alert.setTitle("Create Missing File");
        alert.setHeaderText("The file " + destFile.getName() + " does not exist.");
        alert.setContentText("You can use a template file or create it manually from scratch.\n"
                + "Choose one of the following options:\n\n");
        ButtonType buttonTypeLast = new ButtonType("Copy last used");
        ButtonType buttonTypeTemp = new ButtonType("Copy template");
        ButtonType buttonTypeEmpty = new ButtonType("Create empty file");
        ButtonType buttonTypeCancel = new ButtonType("Cancel", ButtonData.CANCEL_CLOSE);

        alert.getButtonTypes().clear();
        if (lastUsedFile != null) alert.getButtonTypes().add(buttonTypeLast);
        alert.getButtonTypes().addAll(buttonTypeTemp, buttonTypeEmpty, buttonTypeCancel);
        alert.setResizable(true);
        alert.getDialogPane().getChildren().stream().forEach(node -> {
            ((Region)node).setMinWidth(Region.USE_PREF_SIZE);
            ((Region)node).setMinHeight(Region.USE_PREF_SIZE);
        });
        //alert.getDialogPane().setMinWidth(Region.USE_PREF_SIZE);
        //alert.getDialogPane().setPrefWidth(Region.USE_PREF_SIZE);
        
        Optional<ButtonType> result = alert.showAndWait();
        if (result.get() == buttonTypeLast) {
            srcFile = lastUsedFile;
        } else if (result.get() == buttonTypeTemp) {
            srcFile = new File("/usr/share/airtools/" + destFile.getName());
        } else if (result.get() == buttonTypeEmpty) {
            srcFile = new File(destFile.getAbsolutePath());
        } else {
            logger.log("# WARNING: file " + destFile.getName() + " not created");
        }
        if (srcFile != null) {
            try {
                if (srcFile.getAbsolutePath().equals(destFile.getAbsolutePath())) {
                    destFile.createNewFile();
                    logger.log("# created empty file " + destFile.getName());
                } else {
                    Files.copy(srcFile.toPath(), destFile.toPath(),
                        StandardCopyOption.COPY_ATTRIBUTES, StandardCopyOption.REPLACE_EXISTING);
                    logger.log("# file " + srcFile.getAbsolutePath() + " copied to project dir");
                }
            } catch (IOException ex) {
                logger.log("# ERROR: unable to copy file " + srcFile.getAbsolutePath() + " to project dir");
                Logger.getLogger(MainController.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
        
    }    

    
    private void checkDependencies() {
        //logger.log("WARNING: checkDependencies: not implemented yet.");
        int exitCode;
        
        sh.setEnvVars("");
        sh.setArgs("");
        sh.runFunction("check");
        exitCode=sh.getExitCode();
        logger.log("check finished with " + exitCode);
    }
    
    
    private boolean isNewSite (String site) {
        File inFile = null;
        try {
            inFile = new File (projectDir.getValue() + "/sites.dat");
            if (! inFile.exists()) {
                logger.log("WARNING: file " + projectDir.getValue() + "/sites.dat is missing.");
                return true;
            }
            
            SitesList sitesList = new SitesList (inFile, logger);
            if (sitesList.isEmpty()) {
                System.out.println("WARNING: no valid sites found in sites.dat");
                return true;
            } else {
                return ! sitesList.contains(site);
            }
        } catch (Exception ex) {
            Logger.getLogger(NewProjectController.class.getName()).log(Level.SEVERE, null, ex);
        }
        return true;
    }
    
    
    private void openExistingProject() {
        DirectoryChooser dirChooser = new DirectoryChooser();
        File file = null;
        if (! projectDir.getValue().isEmpty())
            file = new File(projectDir.getValue());
        if (file == null || ! file.isDirectory()) {
            file = new File(System.getProperty("user.home"));
        }
        Stage stage = (Stage) appPane.getScene().getWindow();
        dirChooser.setInitialDirectory(file);
        dirChooser.setTitle("Choose existing Project Directory");
        /* note: modal dialog will freeze size of main window
            therefore we pass null (non-modal) instead of stage
        file = dirChooser.showDialog(stage);
        */
        file = dirChooser.showDialog(null);
        if (file != null) {
            // TODO: check for file .airtoolsrc, if missing show a warning message
            projectDir.set(file.getAbsolutePath());
        }
    }
    
    
    private void showOpenProjectDialog() {
        logger.log("# WARNING: use of showOpenProjectDialog is deprecated");
        try {
            FXMLLoader fxmlLoader = new FXMLLoader(getClass().getResource("/tl/airtoolsgui/view/OpenProject.fxml"));
            Parent parent = fxmlLoader.load();
            OpenProjectController dialogController = fxmlLoader.<OpenProjectController>getController();
            dialogController.setReferences(projectDir);
            
            Scene scene = new Scene(parent);
            Stage stage = new Stage();
            stage.initModality(Modality.APPLICATION_MODAL);
            stage.setScene(scene);
            stage.setTitle("Open AIRTOOLS Project");
            stage.showAndWait();
        } catch (IOException ex) {
            Logger.getLogger(MainController.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
    
    
    public void showNewProjectDialog() {
        try {
            FXMLLoader fxmlLoader = new FXMLLoader(getClass().getResource("/tl/airtoolsgui/view/NewProject.fxml"));
            Parent parent = fxmlLoader.load();
            NewProjectController dialogController = fxmlLoader.<NewProjectController>getController();
            dialogController.setReferences(configFile, logger, projectDir, rawDir, tempDir, site, tzoff, observer);
            
            Scene scene = new Scene(parent);
            Stage stage = new Stage();
            stage.initModality(Modality.APPLICATION_MODAL);
            stage.setScene(scene);
            stage.setTitle("New AIRTOOLS Project");
            stage.showAndWait();

            // handle new site entered by the user
            if (isNewSite(site.getValue())) {
                logger.log("# new site = " + site.getValue());
                Alert alert = new Alert(Alert.AlertType.INFORMATION);
                alert.setTitle("New Observatory Site");
                alert.setHeaderText("New site not known to sites parameter file.");
                alert.setContentText("You requested to use a new site. Please edit the\n"
                                + "sites parameter file (choose action from menu\n"
                                + "\"Edit\") and fill in all required fields.\n\n");
                alert.showAndWait();
                // TODO: add line to sites.dat
            }
        } catch (IOException ex) {
            Logger.getLogger(MainController.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
    
    
    public void showWindowArchive() {
        System.out.println("showWindowArchive()");
        if (windowArchive == null) try {
            FXMLLoader fxmlLoader = new FXMLLoader(getClass().getResource("/tl/airtoolsgui/view/Archive.fxml"));
            Parent parent = fxmlLoader.load();
            ArchiveController controller = fxmlLoader.<ArchiveController>getController();
            controller.setReferences(sh, logger, projectDir);

            Scene scene = new Scene(parent);
            windowArchive = new Stage();
            //windowArchive.initModality(Modality.APPLICATION_MODAL);
            windowArchive.setScene(scene);
            windowArchive.setTitle("Archive Project Data");
        } catch (IOException ex) {
            Logger.getLogger(MainController.class.getName()).log(Level.SEVERE, null, ex);
        }
        windowArchive.showAndWait();
    }
    
    
    public void showWindowListResults() {
        System.out.println("showWindowListResults()");
        if (windowListResults == null) try {
            FXMLLoader fxmlLoader = new FXMLLoader(getClass().getResource("/tl/airtoolsgui/view/ListResults.fxml"));
            Parent parent = fxmlLoader.load();
            ListResultsController controller = fxmlLoader.<ListResultsController>getController();
            controller.setReferences(sh, logger, projectDir);

            Scene scene = new Scene(parent);
            windowListResults = new Stage();
            //windowListResults.initModality(Modality.APPLICATION_MODAL);
            windowListResults.setScene(scene);
            windowListResults.setTitle("List Results");
        } catch (IOException ex) {
            Logger.getLogger(MainController.class.getName()).log(Level.SEVERE, null, ex);
        }
        windowListResults.showAndWait();
    }
    
    
    public void showWindowCreateBadpixelMask() {
        System.out.println("showWindowCreateBadpixelMask()");
        if (windowListResults == null) try {
            FXMLLoader fxmlLoader = new FXMLLoader(getClass().getResource("/tl/airtoolsgui/view/CreateBadpixelMask.fxml"));
            Parent parent = fxmlLoader.load();
            CreateBadpixelMaskController controller = fxmlLoader.<CreateBadpixelMaskController>getController();
            controller.setReferences(sh, logger, projectDir);

            Scene scene = new Scene(parent);
            windowCreateBadpixelMask = new Stage();
            //windowListResults.initModality(Modality.APPLICATION_MODAL);
            windowCreateBadpixelMask.setScene(scene);
            windowCreateBadpixelMask.setTitle("Create BadPixel Mask");
        } catch (IOException ex) {
            Logger.getLogger(MainController.class.getName()).log(Level.SEVERE, null, ex);
        }
        windowCreateBadpixelMask.showAndWait();
    }
    
    
    public void showWindowLightCurve() {
        System.out.println("showWindowLightCurve()");
        if (windowLightCurve == null) try {
            FXMLLoader fxmlLoader = new FXMLLoader(getClass().getResource("/tl/airtoolsgui/view/LightCurve.fxml"));
            Parent parent = fxmlLoader.load();
            LightCurveController controller = fxmlLoader.<LightCurveController>getController();
            controller.setReferences(sh, logger, projectDir);

            Scene scene = new Scene(parent);
            windowLightCurve = new Stage();
            //windowLightCurve.initModality(Modality.APPLICATION_MODAL);
            windowLightCurve.setScene(scene);
            windowLightCurve.setTitle("Plot Light Curve");
        } catch (IOException ex) {
            Logger.getLogger(MainController.class.getName()).log(Level.SEVERE, null, ex);
        }
        windowLightCurve.showAndWait();
    }
    
    
    public void showWindowMultiApPhotometry() {
        System.out.println("showWindowMultiApPhotometry()");
        if (windowMultiApPhotometry == null) try {
            FXMLLoader fxmlLoader = new FXMLLoader(getClass().getResource("/tl/airtoolsgui/view/MultiApPhotometry.fxml"));
            Parent parent = fxmlLoader.load();
            MultiApPhotometryController controller = fxmlLoader.<MultiApPhotometryController>getController();
            controller.setReferences(sh, logger, projectDir);

            Scene scene = new Scene(parent);
            windowMultiApPhotometry = new Stage();
            //windowMultiApPhotometry.initModality(Modality.APPLICATION_MODAL);
            windowMultiApPhotometry.setScene(scene);
            windowMultiApPhotometry.setTitle("Multi-Aperture Photometry");
        } catch (IOException ex) {
            Logger.getLogger(MainController.class.getName()).log(Level.SEVERE, null, ex);
        }
        windowMultiApPhotometry.showAndWait();
    }
    
    
    public void showWindowAstrometry() {
        System.out.println("showWindowAstrometry()");
        if (windowAstrometry == null) try {
            FXMLLoader fxmlLoader = new FXMLLoader(getClass().getResource("/tl/airtoolsgui/view/Astrometry.fxml"));
            Parent parent = fxmlLoader.load();
            AstrometryController controller = fxmlLoader.<AstrometryController>getController();
            controller.setReferences(sh, logger, projectDir);

            Scene scene = new Scene(parent);
            windowAstrometry = new Stage();
            //windowAstrometry.initModality(Modality.APPLICATION_MODAL);
            windowAstrometry.setScene(scene);
            windowAstrometry.setTitle("Astrometry");
        } catch (IOException ex) {
            Logger.getLogger(MainController.class.getName()).log(Level.SEVERE, null, ex);
        }
        windowAstrometry.showAndWait();
    }
    
    
    public void showUnknownDialog() {
        try {
            FXMLLoader fxmlLoader = new FXMLLoader(getClass().getResource("/tl/airtoolsgui/view/MultiApPhotometry.fxml"));
            Parent parent = fxmlLoader.load();
            MultiApPhotometryController dialogController = fxmlLoader.<MultiApPhotometryController>getController();
            //multiApPhotometryController.setReferences(logger, projectDir, paramDir, rawDir, tempDir, site, tzoff);
            
            Scene scene = new Scene(parent);
            Stage stage = new Stage();
            stage.initModality(Modality.APPLICATION_MODAL);
            stage.setScene(scene);
            stage.setTitle("Multi-Aperture Photometry");
            stage.showAndWait();
        } catch (IOException ex) {
            Logger.getLogger(MainController.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
    
    
    private void openOnlineManual() {
        System.out.println("openOnlineManual()");
        //ProcessBuilder pb = new ProcessBuilder("/bin/bash", "-c", "xdg-open " + onlineManualURL);
        ProcessBuilder pb = new ProcessBuilder("xdg-open", onlineManualURL);
        try {
            pb.start();
        } catch (IOException ex) {
            Logger.getLogger(MainController.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
    
    
    private void showAboutDialog() {
        int memtot;
        int memused;
        String author="Thomas Lehmann";
        String mail="t_lehmann@freenet.de";
        Date compileTime = null;
        //DateFormat fmt = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.mmm'Z'");
        DateFormat fmt = new SimpleDateFormat("yyyy-MM-dd");

        System.gc();
        memtot = (int) (Runtime.getRuntime().totalMemory()/1024/1024);
        memused = memtot - (int) (Runtime.getRuntime().freeMemory()/1024/1024);
        
        /* determine compilation time (currently not used)
        try {
            String rn = this.getClass().getName().replace('.', '/') + ".class";
            JarURLConnection j = (JarURLConnection) this.getClass().getClassLoader().getResource(rn).openConnection();
            compileTime=new Date(j.getJarFile().getEntry("META-INF/MANIFEST.MF").getTime());
        } catch (IOException e) {
            System.out.println("WARNING: unable to get compilation time");
        }
        */
        
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle("About AIRTOOLS");
        alert.setHeaderText("AIRTOOLS " + progVersion);
        /*
            TODO: show version of airtools.sh and airfun.sh
        */
        Label l1 = new Label("GUI version:  " + progVersion);
        //if (compileTime != null) l1.setText(l1.getText() + "  (" + fmt.format(compileTime) + ")");
        l1.setText(l1.getText() + "  (" + progDate + ")");
        Label l2 = new Label("Java-Runtime: " + System.getProperty("java.version"));
        Label l3 = new Label("Operating System: " + System.getProperty("os.name"));
        Label l4 = new Label("Memory: " + memused + "/" + memtot + " MB");
        Label labelAuthor = new Label("Author: " + author);
        Label labelMail = new Label("E-Mail: " + mail);
        /*
        Button buttonMail = new Button("E-Mail");
        buttonMail.setOnAction((event) -> {
            alert.close();
            mainApp.getHostServices().showDocument("mailto:t_lehmann@freenet.de");
        });
        */
        /*
        HBox hboxMail = new HBox();
        hboxMail.setAlignment(Pos.CENTER_LEFT);
        hboxMail.setSpacing(8);
        hboxMail.getChildren().addAll(labelMail, buttonMail);
        hboxMail.getChildren().addAll(labelMail);
        */
        VBox v = new VBox();
        v.setSpacing(2);
        //v.getChildren().addAll(l1, l2, l3, l4, hboxMail,);
        v.getChildren().addAll(l1, l2, l3, l4, labelAuthor, labelMail);
        alert.getDialogPane().contentProperty().set(v);
        // TODO: increase font size relative to system size
        //alert.getDialogPane().setStyle("-fx-font-size: 14px;");
        alert.showAndWait();
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

    @FXML
    private void onSelectTabImageReduction(Event event) {
        paneImageReductionController.updateTabContent();
    }

    @FXML
    private void onSelectTabCometPhotometry(Event event) {
        paneCometPhotometryController.updateTabContent();
    }

    @FXML
    private void onSelectTabMiscTools(Event event) {
    }
}
