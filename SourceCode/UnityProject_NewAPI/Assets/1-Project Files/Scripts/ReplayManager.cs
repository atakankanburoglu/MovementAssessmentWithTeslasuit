using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using UnityEngine.UI;
using Newtonsoft.Json;

public class ReplayManager : MonoBehaviour
{
    string path;
    public TsHumanAnimator tsHumanAnimator;

    private bool isReplayPlaying;

    //Coroutine vars
    private IEnumerator coroutine;
    private bool coroutineRunning;
    private int currentIndex = 0;

    [SerializeField]
    private Dropdown replayDropDown;
    [SerializeField] 
    private Button replayButton;
    [SerializeField]
    private Slider replayBar;
    public Sprite Play;
    public Sprite Pause;


    void Start()
    {
        path = Application.dataPath + "/JsonAttempts/";
        FillReplayDropDown();
    }

    public void FillReplayDropDown()
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

    public void OptionChosenFromDropDown()
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

        int frameCount = player.Count;
        replayBar.maxValue = frameCount;

        while (currentIndex < frameCount)
        {
            yield return new WaitUntil(() => isReplayPlaying == true);
            tsHumanAnimator.ReplayUpdate(player[currentIndex]);
            yield return new WaitForEndOfFrame();
            currentIndex += 1;
            replayBar.value = currentIndex;
        }
       
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
   
    public void StopReplay()
    {
        isReplayPlaying = false;
    }

}
