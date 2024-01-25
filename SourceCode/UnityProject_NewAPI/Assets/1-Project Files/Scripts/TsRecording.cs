using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TsAPI.Types;
using TsSDK;
using System.IO;
using UnityEngine.UI;
using TMPro;
using Newtonsoft.Json;
using System.Runtime.Serialization;
using System;

public class TsRecording : MonoBehaviour
{
    string path; //@"C:\StudentProjects\Burakhan\Tesla Suit\Assets\JsonAttempts\";
    string underScore = "_";
    public TMP_InputField inputName;
    public TsHumanAnimator tsHumanAnimator;

    private bool shouldSave;
    private bool isReplayPlaying;
    private float timeInterval = 0.5f;

    private ReplayObject infoToJSon;

    //Coroutine vars
    private IEnumerator coroutine;
    private bool coroutineRunning;
    private int currentIndex = 0;

    //UI Stuff
    [SerializeField]
    private Dropdown replayDropDown;
    [SerializeField]
    private Dropdown trainingTypeDropDown;
    [SerializeField] 
    private Button replayButton;
    [SerializeField]
    private Slider replayBar;
    [SerializeField]
    private GameObject createSubjectField;
    [SerializeField]
    private GameObject startRecordingField;
    public Sprite Play;
    public Sprite Pause;

    //Python Communication
    private DataGateway dataGateway;

    float timer;

  
    void Start()
    {
        path = Application.dataPath + "/JsonAttempts/";

        dataGateway = FindObjectOfType<DataGateway>();
        //CsvEditor.DetectCSV();
        FillReplayDropDown();
        FillTrainingDropDown();
    }
   

    // Update is called once per frame
    void Update()
    {
        timer += Time.deltaTime;
        if (shouldSave && timer >timeInterval)
        {
            //Do this for Replay
            ReplayInfo rp = new ReplayInfo();
            foreach (KeyValuePair<TsHumanBoneIndex, Transform> kvp in tsHumanAnimator.BoneTransforms)
            {
                rp.replayPosition.Add(kvp.Key, kvp.Value.position);
                rp.replayRotation.Add(kvp.Key, kvp.Value.rotation.eulerAngles);
                rp.replayRotationQuaternion.Add(kvp.Key, MyQuaternion.ConverToMyQuat(kvp.Value.rotation));
            }

            infoToJSon.replayInfo.Add(rp);

            //Do this for Model Training/Testing
            TrainingType trainingType = (TrainingType)Enum.Parse(typeof(TrainingType), trainingTypeDropDown.options[trainingTypeDropDown.value].text);
            ImuDataObject imuDataObject = new ImuDataObject(trainingType, tsHumanAnimator.ImuData, Time.time);
            dataGateway.PythonClient.pushSuitData(imuDataObject);
           
        }
        //Movement recording needs to start with a delay, so that the starting pose could be assumed. 
        //timer=0;
       

        //foreach (KeyValuePair<TsHumanBoneIndex, Transform> kvp in avatarBoneInfo.BoneTransforms)
        //{
        //    Debug.Log("index: " + kvp.Key + " pos: " + kvp.Value.position + " pos: " + kvp.Value.rotation);
        //}
    }

    void FillReplayDropDown()
    {
        //Get all Jsons
        DirectoryInfo dir = new System.IO.DirectoryInfo(path);
        Debug.Log("datapath: " + path);
        List<string> filenames = new List<string>();
        foreach(FileInfo f in dir.GetFiles())
        {
            string St = f.Name;
            //dont consider meta data they are for git
            if (St.Contains("meta")) continue;

            int pTo = St.IndexOf(".json");
           filenames.Add( St.Substring(0, pTo));
    
        }

        replayDropDown.ClearOptions();
        replayDropDown.AddOptions(filenames);  

    }
    void FillTrainingDropDown()
    {
        string[] names = Enum.GetNames(typeof(TrainingType));
        trainingTypeDropDown.ClearOptions();
        trainingTypeDropDown.AddOptions(new List<string>(names));
    }

    public void CreateNewSubject()
    {
        if (inputName.text == string.Empty) { Debug.LogError("Please enter a name for this subject"); return; }
        infoToJSon = new ReplayObject() { subjectName = inputName.text, trainingType = (TrainingType)Enum.Parse(typeof(TrainingType), trainingTypeDropDown.options[trainingTypeDropDown.value].text) };
        startRecordingField.SetActive(true);
        createSubjectField.SetActive(false);

    
        Debug.Log("object created");
    }
    public void StartSaving()
    {
        if (infoToJSon == null) return;
        shouldSave = true;
    }
    public void StopSaving()
    {
        shouldSave = false;
    }
    public void CreateJSon()
    {
        if (!shouldSave)
        {
            Debug.Log("json");
            //string output = JsonUtility.ToJson(infoToJSon);
            //File.WriteAllText(Application.dataPath + $"/{infoToJSon.subjectName}_replayInfos.txt", output);
            string json = JsonConvert.SerializeObject(infoToJSon.replayInfo.ToArray(),Formatting.Indented);

            //write string to file
            System.IO.File.WriteAllText(string.Concat(path, $"{infoToJSon.subjectName}",underScore, $"{ infoToJSon.trainingType.ToString() }", ".json"), json);
            infoToJSon = null;
        }
        FillReplayDropDown();
    }
    //referenced on scene object
    public void OptionChosenFromDropDown()
    {
        if(coroutineRunning)StopCoroutine(coroutine);
        coroutineRunning = false;
        replayButton.image.sprite = Play;
        replayBar.value = 0;
        currentIndex = 0;
        isReplayPlaying = false;
        tsHumanAnimator.Replay = false;
    }

    public void FreeLook()
    {
        if (coroutineRunning) StopCoroutine(coroutine);
        coroutineRunning = false;
        replayButton.image.sprite = Play;
        replayBar.value = 0;
        currentIndex = 0;
        isReplayPlaying = false;
        tsHumanAnimator.Replay = false;
    }
    public void Replay()
    {
        shouldSave = false;
        if (coroutineRunning) return;
        coroutine = Replayy();
        tsHumanAnimator.Replay = true;
        StartCoroutine(coroutine);

    }

    public IEnumerator Replayy()
    {
        coroutineRunning = true;


        string name = replayDropDown.options[replayDropDown.value].text;
        string jsonArr = File.ReadAllText(string.Concat(path, $"{name}", ".json"));
        var player = JsonConvert.DeserializeObject<List<ReplayInfo>>(jsonArr);

        #region Interpolation attempt - Ignore
        ////Interpolation Attempt- Ignore this part
        //List<ReplayInfo> slowplayer = new List<ReplayInfo>();
        //for (int i =0; i < player.Count; i++)
        //{
        //    if (i % 2 == 0) slowplayer.Add(player[i]);
        //    else
        //    {
        //        if (player[i + 1] != null) slowplayer.Add(ReplayInfo.Interpolate(player[i - 1], player[i + 1]));
        //        else slowplayer.Add(ReplayInfo.Interpolate(player[i - 1], player[i ]));
        //    }
        //}
        #endregion
        // int frameCount = infoToJSon.replayInfo.Count;
        int frameCount = player.Count;
        //int frameCount = slowplayer.Count;
        replayBar.maxValue = frameCount;

        //normal play
        while (currentIndex < frameCount)
        {
            yield return new WaitUntil(() => isReplayPlaying == true);
            tsHumanAnimator.ReplayUpdate(player[currentIndex]);
            yield return new WaitForEndOfFrame();
            currentIndex += 1;
            replayBar.value = currentIndex;
        }
        ////fastplay
        //while (currentIndex+1 < frameCount)
        //{
        //    yield return new WaitUntil(() => isReplayPlaying == true);
        //    avatarBoneInfo.ReplayUpdate(player[currentIndex]);
        //    yield return new WaitForEndOfFrame();
        //    currentIndex +=2;
        //    replayBar.value = currentIndex;
        //}
        ////slow play
        //while (currentIndex < frameCount)
        //{
        //    yield return new WaitUntil(() => isReplayPlaying == true);
        //    avatarBoneInfo.ReplayUpdate(slowplayer[currentIndex]);
        //    yield return new WaitForEndOfFrame();
        //    yield return new WaitForSeconds(0.01f);
        //    currentIndex += 1;
        //    replayBar.value = currentIndex;
        //}
        yield return null;

        coroutineRunning = false;
        replayButton.image.sprite = Play;
        replayBar.value = 0;
        currentIndex = 0;
        tsHumanAnimator.Replay = false;

    }
    //used in the editor
    public void SliderValueChanged()
    {
        currentIndex = (int)replayBar.value;
    }

    public void PlayPauseReplay()
    {
        isReplayPlaying = !isReplayPlaying;

        if (isReplayPlaying) replayButton.image.sprite = Pause;
        else replayButton.image.sprite = Play;
    }
   
}
