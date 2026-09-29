using System.ComponentModel;

namespace Jellyfin.Plugin.MetaTube.Translation;

public enum TranslationEngine
{
    [Description("百度")]
    Baidu,

    [Description("Google（付费版）")]
    Google,

    [Description("Google（免费版）")]
    GoogleFree,

    [Description("DeepL")]
    DeepL,

    [Description("OpenAI")]
    OpenAi
}