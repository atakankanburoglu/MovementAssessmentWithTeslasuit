using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ReplayObject
{
    public string subjectName;
    public List<ReplayInfo> replayInfo = new List<ReplayInfo>();
    public ExerciseType exerciseType = ExerciseType.PLANKHOLD;

    public ReplayObject() { }
    public ReplayObject(string name, List<ReplayInfo> info, ExerciseType training)
    {
        subjectName = name;
        replayInfo = info;
        exerciseType = training;
    }
    // public List<float> timeStamp;   
}