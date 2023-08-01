<script>
  import { locale } from '$lib/translations'

  export let value

	$: formattedNumber = Number(value).toLocaleString(locale, {
		notation: 'compact',
		compactDisplay: 'short'
	})
</script>

<span>{formattedNumber}</span>

<style>
	span {
		font-variant-numeric: tabular-nums;
	}
</style>
